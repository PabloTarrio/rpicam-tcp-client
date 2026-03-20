"""
EJEMPLO 07 - Detector de color en tiempo real

OBJETIVO:
    Detectar y rastrear objetos por color en tiempo real usando el espacio
    de color HSV, segmentación con cv2.inRange() y cálculo del centroide
    con cv2.moments()

REQUISITOS_PREVIOS:
    - Completar ejemplos básicos e intermedios
    - Entender bucle básico de recepción de frames (CameraClient)
    - Conocer qué es un espacio de color (BGR vs HSV)

CONCEPTOS QUE APRENDERÁS:
    - Por qué HSV es mejor que BGR para detectar colores
    - Conversión de espacio de color: cv2.cvtColor() con COLOR_BGR2HSV()
    - Creación de máscara binaria con cv2.inRange()
    - Cálculo del centroide de unobjeto con cv2.moments()
    - Dibujo de contornos y anotaciones sobre el frame

CASOS DE USO PRÁCTICOS:
    - Seguimiento de objetos de color conocido (robótica, automatización)
    - Detección de señales de color en entornos controlados
    - Base para sistemas de visión artificial más complejos

TIEMPO ESTIMADO: 30 minutos

DETENER: Pulsa 'q' en la ventana para salir.
"""

import argparse

import cv2
import numpy as np

from rpicam_tcp_client import CameraClient


def main():
    """
    Función principal del detector de color

    Flujo de programa:
        1. Parsear argumentos (host, puerto, color, resolución)
        2. Definir rangos HSV para el color seleccionado
        3. Crear CameraClient y conectar con la Raspberry Pi
        4. Bucle de captura:
            - Obtener frame con cam.get_frame()
            - Convertir BGR -> HSV con cv2.cvtColor()
            - Crear máscara binaria con cv2.cvtinRange()
            - Calcular centroide con cv2.moments()
            - Mostrar resultados con cv2.imshow
        5. Salir con 'q' y cerrar ventana limpiamente.
    """

    # ===============================================================
    # PASO 1: Parsear argumentos de la linea de comandos
    # ===============================================================
    parser = argparse.ArgumentParser(
        description="Detecta y rastrea objetos por color en tiempo real."
    )
    parser.add_argument(
        "--host",
        required=True,
        help="IP de la Raspberry PI",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5001,
        help="Puerto TCP (por defecto: 5001)",
    )
    parser.add_argument(
        "--color",
        default="rojo",
        choices=["rojo", "verde", "azul", "amarillo"],
        help="Color a detectar (por defecto: rojo)",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=640,
        help="Ancho del frame en el cliente (por defecto: 640)",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=480,
        help="Alto del frame en el cliente (por defecto: 480)",
    )
    parser.add_argument(
        "--rotation",
        type=int,
        default=180,
        choices=[0, 90, 180, 270],
        help="Rotación de la imagen [0, 90, 180, 270] (por defecto 180)"
    )
    parser.add_argument(
        "--saturation",
        type=float,
        default=0.6,
        help="Saturación de la imagen (por defecto 0.6)"
    )
    args = parser.parse_args()
    
    # ===============================================================
    # PASO 2: Definir rangos HSV para el color seleccionado
    #   Cada color se define con dos arrays numpy: limite inferior y superior
    #   en el espacio HSV (Hue 0-179, Saturation 0-255, Value 0,255)
    # ===============================================================

    rangos_hsv = {
        "rojo": (np.array([0, 120, 70]), np.array([10, 255, 255])),
        "verde": (np.array([36, 100, 100]), np.array([86, 255, 255])),
        "azul": (np.array([100, 150, 50]), np.array([140, 255, 255])),
        "amarillo": (np.array([20, 100, 100]), np.array([35, 255, 255])),
    }
    limite_inferior, limite_superior = rangos_hsv[args.color]

    # ===============================================================
    # PASO 3: Crear CameraClient y conectar con Raspberry Pi.
    # ===============================================================
    with CameraClient(
        host= args.host,
        port= args.port,
        width= args.width,
        height= args.height,
        rotation= args.rotation,
        saturation= args.saturation,
    ) as cam:
        print(f"Conectado a la cámara en {args.host}:{args.port}")
        print(f"Detectando color: {args.color}. Pulsa 'q' para salir.")

        # ===============================================================
        # PASO 4: Bucle principal de captura y detección
        # ===============================================================
        cv2.namedWindow("Detector de color", cv2.WINDOW_NORMAL)
        cv2.namedWindow("Máscara", cv2.WINDOW_NORMAL)
        try:

            while True:
                frame = cam.get_frame()
                if frame is None:
                    print("Conexión perdida")
                    break
                # 4.1 Convertir BGR -> HSV
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                # 4.2 Crear máscara binaria con cv2.inRange()
                mascara = cv2.inRange(hsv, limite_inferior, limite_superior)
                
                # 4.3 Calcular el centroide con cv2.moments()
                momentos = cv2.moments(mascara)
                print(f"m00 = {momentos['m00']:.0f}")

                if momentos["m00"] > 0:
                    cx = int(momentos["m10"] / momentos["m00"])
                    cy = int(momentos["m01"] / momentos["m00"])

                    # 4-4 Dibujar centroide y anotación sobre el frame
                    cv2.circle(
                        img=frame,
                        center=(cx, cy),
                        radius=10,
                        color=(0, 255, 0),
                        thickness=-1
                    )
                    cv2.putText(
                        img=frame,
                        text=f"{args.color} ({cx}, {cy})",
                        org=(cx + 15, cy),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=0.6,
                        color=(0, 255, 0),
                        thickness=2,
                    )

                cv2.imshow("Detector de color", frame)
                cv2.imshow("Máscara", mascara)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

        except KeyboardInterrupt:
            print("\nDetección solicitada por el usuario.")
        
        finally:
            # ===============================================================
            # PASO 5: Cerrar ventanas al salir
            # ===============================================================
            cv2.destroyAllWindows()


if __name__ == "__main__":
    main()