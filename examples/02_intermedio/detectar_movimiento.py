"""
EJEMPLO 5 -  Detección de movimiento en tiempo real

Tutorial paso a paso para visión artificial básica con OpenCV

OBJETIVO:
    Detectar movimiento en la imagen de la Raspberry Pi Camera en tiempo real.
    Resaltar zonas con cambios mediante contornos y alertas visuales.

REQUISITOS PREVIOS:
    - Completar ejemplos 1 y 2 (mostrar_video.py, mostrar_video_configurado.py)
    - Entender bucles infinitos y context managers
    - Conocer cv2.imshow básico

CONCEPTOS CLAVE:
    - Background Subtraction: comparar frame actual vs fondo aprendido
    - cv2.createBackgroundSubtractorMOG2(): modelo estadístico de fondo
    - cv2.findContours(): detectar regiones con cambios
    - cv2.boundingRect(): dibujar caja alrededor del movimiento
    - Umbral de área mínima: filtrar ruido (cambios insignificantes)

CASOS DE USO:
    - Vigilancia y seguridad
    - Detección de presencia para robots móviles
    - Trigger automático para grabar_video.py
    - Conteo de objetos en movimiento
    - Experimentos de visión artificial en robótica

TIEMPO ESTIMADO:
    - 20 minutos

DETENER:
    - Pulsa 'q' en la ventana para salir.
"""

import argparse

import cv2

from rpicam_tcp_client import CameraClient


def main():
    """
    Función principal: conecta, detecta movimiento, desconecta

    Flujo del programa (PASO A PASO):

    1. Parsear argumentos (--host, --area-minima, --umbral)
    2. Crear BackgroundSubtractor (modelo estadístico del fondo)
    3. Context manager CameraClient
    4. Bucle: frame -> mascara -> contornos -> dibujar -> mostrar
    5. Salir limpiamente con 'q'
    """

    # ===============================================================
    # PASO 1: argparse parámetro detección
    # ===============================================================
    parser = argparse.ArgumentParser(
        description="Detecta movimiento en tiempo real desde RPi Camera"
    )

    parser.add_argument("--host", required=True, help="IP Raspberry Pi")
    parser.add_argument("--port", type=int, default=5001, help="Puerto TCP")
    parser.add_argument(
        "--area_minima",
        type=int,
        default=500,
        help="Area mínima px2 para considerar movimiento (default 500)",
    )
    parser.add_argument(
        "--umbral",
        type=int,
        default=25,
        help="Sensibilidad detección 1-100, menor= mas sensible (default 25)",
    )
    parser.add_argument(
        "--width", type=int, default=640, help="Ancho del frame (default 640)"
    )
    parser.add_argument(
        "--height", type=int, default=480, help="Alto del frame (default 480)"
    )
    parser.add_argument(
        "--rotation",
        type=int,
        default=0,
        choices=[0, 90, 180, 270],
        help="Rotación grados (default 0)",
    )
    args = parser.parse_args()

    # ===============================================================
    # PASO 2: crear BackgroundSubtractor
    # ===============================================================
    subtractor = cv2.createBackgroundSubtractorMOG2(
        history=500,
        varThreshold=args.umbral,
        detectShadows=False,
    )

    # ===============================================================
    # PASO 3: conectar cámara
    # ===============================================================
    cam = CameraClient(
        host=args.host,
        port=args.port,
        width=args.width,
        height=args.height,
        rotation=args.rotation,
    )

    with cam:
        print("Detectando movimiento. Pulsa 'q' para salir.")
        print(f"Área mínima: {args.area_minima}px2 | Umbral: {args.umbral}")
        cv2.namedWindow("Cámara", cv2.WINDOW_NORMAL)
        cv2.namedWindow("Máscara", cv2.WINDOW_NORMAL)

        while True:
            frame = cam.get_frame()
            if frame is None:
                print("Conexión perdida")
                break

            # ===============================================================
            # PASO 4: Aplicar BackgroundSubtractor
            # Devuelve mascara: blanco=movimiento, negro=fondo
            # ===============================================================
            mascara = subtractor.apply(frame)

            # ===============================================================
            # PASO 5: Encontrar contornos en la mascara
            # ===============================================================
            contornos, _ = cv2.findContours(
                image=mascara, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE
            )

            # ===============================================================
            # PASO 6: Filtrar contornos por area mínima y dibujar
            # ===============================================================
            movimiento_detectado = False
            for contorno in contornos:
                area = cv2.contourArea(contorno)
                if area < args.area_minima:
                    continue

                # Dibujar caja roja alrededor del movimiento
                x, y, w, h = cv2.boundingRect(contorno)
                cv2.rectangle(
                    img=frame,
                    pt1=(x, y),
                    pt2=(x + w, y + h),
                    color=(0, 0, 255),
                    thickness=2,
                )
                movimiento_detectado = True

            # ===============================================================
            # PASO 7: Mostrar alerta visual si hay movimiento
            # ===============================================================
            if movimiento_detectado:
                cv2.putText(
                    img=frame,
                    text="MOVIMIENTO DETECTADO",
                    org=(10, 30),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=1,
                    color=(0, 0, 255),
                    thickness=2,
                )
            else:
                cv2.putText(
                    img=frame,
                    text="Sin movimiento",
                    org=(10, 30),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.8,
                    color=(0, 255, 0),
                    thickness=2,
                )

            # ===============================================================
            # PASO 8: Mostrar frame y mascara
            # ===============================================================
            cv2.imshow("Cámara", frame)
            cv2.imshow("Máscara", mascara)

            # Controles de la grabación ('q'= fin)
            if cv2.waitKey(delay=1) & 0xFF == ord("q"):
                break

        cv2.destroyAllWindows()

# ===============================================================
# EJERCICIOS para practicar
# ===============================================================
# 1. Sensibilidad: Prueba --umbral 5 y --umbral 50.
#    Que diferencia observas en la mascara? Cuando hay demasiado ruido?
# 2. Area minima: Prueba --area-minima 100 y --area-minima 2000.
#    Que objetos desaparecen al aumentar el area minima?
# 3. Contar objetos: Modifica el bucle para contar cuantos contornos
#    superan el area minima e imprimir el numero en pantalla.
#    PISTA: usa una variable contador antes del for.
# 4. Guardar capturas: Cuando se detecte movimiento, guarda el frame
#    automaticamente con cv2.imwrite() y timestamp en el nombre.
#    PISTA: combina con datetime.now().strftime().
# 5. Trigger para grabar: Modifica grabar_video.py para que solo
#    empiece a grabar cuando detectar_movimiento.py detecte actividad.
#    PISTA: cv2.createBackgroundSubtractorMOG2 puede usarse en ambos.
# 6. RETO AVANZADO: Los primeros frames siempre detectan movimiento
#    porque el BackgroundSubtractor necesita aprender el fondo.
#    Cuantos frames necesita para estabilizarse?
#    Modifica el codigo para ignorar los primeros N frames.
#    PISTA: usa un contador frame_count y una condicion if frame_count > N.
# ===============================================================

if __name__ == "__main__":
    main()
