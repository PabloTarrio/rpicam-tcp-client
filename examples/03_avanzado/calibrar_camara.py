"""
EJEMPLO 08 - Calibración de cámara con tablero de ajedrez

OBJETIVO:
    Calcular la matriz intrínseca y los coeficientes de distorsión
    de la Raspberry Pi Camera Module 2 NoIR usando un tablero de
    ajedrez y el algoritmo de calibración de OpenCV

REQUISITOS PREVIOS:
    - Haber completado los ejemplos básicos e intermedios
    - Entender el bucle básico de recepción de frames (CameraClient)
    - Tener impreso o en pantalla un tabledo de ajedrez (9x6 esquinas)

CONCEPTOS QUE APRENDERÁS:
    - Qué es la matriz intrínseca de una cámara (focal, centro óptico)
    - QUé son los coeficientes de distorsión radial y tangencial
    - Detección autmática de esquinas con cv2.findChessboardCorners()
    - Refinamiento subpixel con cv2.cornerSubPix()

CASOS DE USO PRÁCTICOS:
    - Prerrequisito para medir distancias reales con la cámara
    - Corrección de distorisión en imágenes y video
    - Base de sistemas de vision 3D y realidad aumentada

TIEMPO ESTIMADO: 45 minutos

DETENER: Pulsa 'q' para salida, 'c' para capturar una imagen de calibración
"""

import argparse

import cv2
import numpy as np

from rpicam_tcp_client import CameraClient


def main():
    """
    Función principal del proceso de calibración

    Flujo del programa:
        1. Parsear argumentos (host, puerto, resolución, esquinas)
        2. Preparar puntos 3D del tablero de ajedrez
        3. Crear CameraClient y conectar con la Raspberry Pi
        4. Bucle de captura:
            - Obtener frame con cam.get_frame()
            - Detectar esquinas con cv2.findChessboardCorners()
            - Refinar con cv2.cornerSubPix()
            - Acumular puntos hasta tener suficientes capturas
        5.Calcular calibración con cv2.calibrateCamera()
        6.Guardar resultados en archivo .npz
    """
    # ===============================================================
    # PASO 1 - Parsear argumentos de la linea de comandos
    # ===============================================================
    parser = argparse.ArgumentParser(
        description="Calibra la cámara usando un tablero de ajedrez"
    )
    parser.add_argument(
        "--host",
        required=True,
        help="IP de la Raspberry Pi",
    )
    parser.add_argument(
        "--port", type=int, default=5001, help="Puerto TCP(por defecto: 5001)"
    )
    parser.add_argument(
        "--width",
        type=int,
        default=640,
        help="Ancho del frame (por defecto: 640)",
    )
    parser.add_argument(
        "--height", type=int, default=480, help="Alto del frame (por defecto: 480)"
    )
    parser.add_argument(
        "--esquinas-x",
        type=int,
        default=9,
        help="Numero de esquinas interiores horizontales (por defecto: 9)",
    )
    parser.add_argument(
        "--esquinas-y",
        type=int,
        default=6,
        help="Número de esquinas interiores verticales (por defecto: 6)",
    )
    parser.add_argument(
        "--capturas",
        type=int,
        default=20,
        help="Numero de capturas necesarias para calibrar (por defecto: 20)",
    )
    parser.add_argument(
        "--salida",
        default="calib_camara.npz",
        help="Archivo de salida con los parámetros"
        "por defecto: 'calib_camara.npz'",
    )
    args = parser.parse_args()

    # ===============================================================
    # PASO 2 - Preparar puntos 3D del tablero de ajedrez
    # Los puntos 3D representan las esquinas del tablero en el mundo
    # real, asumiendo que el tablero está en el plano Z=0.
    # Cada esquina tiene coordenadas (x, y, 0), donde x e y son
    # números enteros que representan la posición en el tablero.
    # ===============================================================
    puntos_3d_tablero = np.zeros(
        (args.esquinas_x * args.esquinas_y, 3), dtype=np.float32
    )
    puntos_3d_tablero[:, :2] = np.mgrid[
        0 : args.esquinas_x, 0 : args.esquinas_y
    ].T.reshape(-1, 2)

    # Listas donde acumularemos los puntos de cada captura válida
    lista_puntos_3d = []  # Puntos del mundo real (siempre el mismo tablero)
    lista_puntos_2d = []  # Puntos detectados en la imagen (cambian en cada
    #     captura)

    # ===============================================================
    # PASO 3 - Crear Camera Client y conectar con la Raspberry Pi
    # Usamos resolución reducida (640x480) para mayor velocidad de
    # procesamiento. La calibración será válida para esta resolución.
    # ===============================================================
    with CameraClient(
        host=args.host,
        port=args.port,
        width=args.width,
        height=args.height,
    ) as cam:
        print(f"Conectado a la cámara en {args.host}:{args.port}")
        print(f"Capturas necesarias: {args.capturas}")
        print("Pulsa 'c' para capturar - 'q' para salir.")

        cv2.namedWindow("Calibración", cv2.WINDOW_NORMAL)

        try:
            while True:
                frame = cam.get_frame()
                if frame is None:
                    print("Conexión perdida")
                    break
                # =========================================================
                # PASO 4.1 - Convertir a escala de grises
                # findChessboardCorners trabaja sobre imagen en grises,
                # no necesita información de colores para detectar esquinas
                # =========================================================
                gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                # =========================================================
                # PASO 4.2 - Detectar esquinas del tablero de ajedrez
                # Devuelve (encontrado, esquinas): encontrado es True/False
                # y esquinas es un array con las coordenadas 2D detectadas
                # =========================================================
                encontrado, esquinas = cv2.findChessboardCorners(
                    image=gris,
                    patternSize=(args.esquinas_x, args.esquinas_y),
                    corners=None,
                )
                # =========================================================
                # PASO 4.3 - Si se detectan esquinas, dibujarlas en verde
                # drawChessboardCorners dibuja las esquinas sobre el frame
                # para que el usuario vea si el tablero está bien enfocado
                # =========================================================
                frame_viz = frame.copy()
                if encontrado:
                    cv2.drawChessboardCorners(
                        image=frame_viz,
                        patternSize=(args.esquinas_x, args.esquinas_y),
                        corners=esquinas,
                        patternWasFound=encontrado,
                    )
                # Mostrar contador de capturas acumuladas
                cv2.putText(
                    img=frame_viz,
                    text=f"Capturas: {len(lista_puntos_2d)}/{args.capturas}",
                    org=(10, 30),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.8,
                    color=(0, 255, 0),
                    thickness=2,
                )
                cv2.imshow("Calibración", frame_viz)

                # =========================================================
                # PASO 4.4 - Capturar al pulsar 'c' si el tablero es visible
                # =========================================================
                tecla = cv2.waitKey(1) & 0xFF
                if tecla == ord("c") and encontrado:
                    # Refinar posición de esquinas a nivel subpixel
                    esquinas_refinadas = cv2.cornerSubPix(
                        image=gris,
                        corners=esquinas,
                        winSize=(11, 11),
                        zeroZone=(-1, -1),
                        criteria=(
                            cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
                            30,
                            0.001,
                        ),
                    )
                    lista_puntos_3d.append(puntos_3d_tablero)
                    lista_puntos_2d.append(esquinas_refinadas)
                    print(f"Captura {len(lista_puntos_2d)}/{args.capturas} registrada.")

                    if len(lista_puntos_2d) >= args.capturas:
                        print("Capturas completadas. Calculando calibración...")
                        break

                elif tecla == ord("q"):
                    print("Salida solicitada por el usuario.")
                    break
        except KeyboardInterrupt:
            print("\nDetección solicitada por el usuario.")

        finally:
            # =========================================================
            # PASO 5 - Cerrar ventana
            # =========================================================
            cv2.destroyAllWindows()
    
    # =================================================================
    # PASO 6 - Calcular calibración y guardar resultados
    # Solo calculamos si se acumularon suficientes capturas válidas
    # calibrateCamera deveulve matriz intrínseca K y los
    # coeficientes de distorsión, además del error de reproyección
    # =================================================================
    if len(lista_puntos_2d) < 2:
        print("No hay suficientes capturas para calibrar. Saliendo.")
        return
    
    print("Calculando parámetros de calibración...")
    error, matriz_k, coef_distorsion, _, _ = cv2.calibrateCamera(
        objectPoints=lista_puntos_3d,
        imagePoints=lista_puntos_2d,
        imageSize=(args.width, args.height),
        cameraMatrix=None,
        distCoeffs=None,
    )

    # =================================================================
    # PASO 7 - Guardar resultados en archivo .npz
    # El archivo .npz permite cargar la calibración en otros scripts
    # (como medir_distancia_visual.py) sin repetir el proceso
    # =================================================================
    np.savez(
        file=args.salida,
        matriz_k=matriz_k,
        coef_distorsion=coef_distorsion,
    )

    print(f"Calibración guardada en: {args.salida}")
    # Matriz de reproyección: Distancia media en píxeles entre las esquinas
    #   reales detectadas y las esquinas que el modelos calibrado predice.
    #   si error < 1.0 se considera calibración de buena calidad.
    print(f"Error de reproyeccion: {error:.4f} pixeles")
    print("Matriz intrínseca K:")
    print(matriz_k)


if __name__ == "__main__":
    main()
