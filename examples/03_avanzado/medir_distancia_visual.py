"""
EJEMPLO 09 - Medición de la distancia visual con cámara calibrada

OBJETIVO:
    Estimar la distancia a un objetode tamaño conocido en tiempo real
    combinando la calibración de cámara (matriz intrínseca K) con la
    detección de objetos por color usando el espacio HSV.

REQUISITOS PREVIOS:
    - Haber completado calibrar_camara.py y tener calibracion.npz
    - Entender la detección por color de detector_color.py
    - Conocer el tamaño real en cm. del objeto a medir

CONCEPTOS QUE APRENDERÁS:
    - Cargar parámetros de calibración desde archivo .npz
    - Extraer la distancia focal f de la matriz intrínseca K
    - Medir el ancho en píxeles de un objeto con cv2.boundingRect()
    - Aplicar la fórmula de triángulos similares: D = (W * f) / P
    - Mostrar la distancia estimada en tiempo real sobre el frame

CASOS DE USO PRÁCTICO:
    - Estimación de distancia a objetos en robótica móvil
    - Control de proximidad sin sensor de distancia dedicado
    - Base para sistemas de navegación visual

TIEMPO ESTIMADO: 30 minutos

DETENER: Pulsa 'q' en la ventana para salir.
"""

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

from rpicam_tcp_client import CameraClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config_loader import load_config


def main():
    """
    Función principal de medición de distancia visual.

    Flujo de programa:
        1. Parsear argumentos (host, puerto, color, ancho real, alto real)
        2. Cargar matriz intrínseca K desde el archivo .npz
        3. Extraer distancia focal f de la matriz K
        4. Crear CameraClient y conectar con la Raspberry Pi.
        5. Bucle de captura:
            - Obtener frame con cam.get_frame()
            - Detectar objeto por color con cv2.inRange()
            - Medir ancho en píxeles con cv2.boundingRect()
            - Calcular distancia D = (W x f) / P
            - Mostrar distancia anotada sobre el frame
        6. Salir con 'q' y cerrar ventana limpiamente
    """
    # =========================================================================
    # PASO 1: Cargar configuración desde config.json (si existe)
    # =========================================================================
    cfg = load_config()
    cfg_conexion = cfg.get("conexion", {})
    cfg_camara = cfg.get("camara", {})
    cfg_calibracion = cfg.get("calibracion", {})
    cfg_distancia_visual = cfg.get("distancia_visual", {})

    # =========================================================================
    # PASO 2. Parsear argumentos de linea de comandos
    # =========================================================================
    parser = argparse.ArgumentParser(
        description="Mide la distancia a un objeto usando la cámara calibrada"
    )
    parser.add_argument(
        "--host",
        default=cfg_conexion.get("host"),
        help="IP Raspberry Pi",
    )
    parser.add_argument(
        "--port", type=int, default=cfg_conexion.get("port", 5001), help="Puerto TCP"
    )
    parser.add_argument(
        "--width", type=int, default=cfg_camara.get("width", 640), help="Ancho frame"
    )
    parser.add_argument(
        "--height", type=int, default=cfg_camara.get("height", 480), help="Alto frame"
    )
    parser.add_argument(
        "--color",
        default=cfg_distancia_visual.get("color", "rojo"),
        choices=["rojo", "azul", "verde", "amarillo"],
        help="Color del objeto a detectar (por defecto: rojo)",
    )
    parser.add_argument(
        "--ancho_real_cm",
        type=float,
        default=cfg_distancia_visual.get("ancho_real_cm", 10.0),
        help="Ancho real del objeto en cm (obligatorio)",
    )
    parser.add_argument(
        "--calibracion",
        default=cfg_calibracion.get("output_file", "calibracion.npz"),
        help="Ruta al archivo de calibración (por defecto: calibracion.npz)",
    )
    parser.add_argument(
        "--rotation",
        type=int,
        default=cfg_camara.get("rotation", 180),
        choices=[0, 90, 180, 270],
        help="Rotación del frame en el cliente (por defecto: 0)",
    )
    args = parser.parse_args()

    if args.host is None:
        print("Error: indica --host o configura 'host' en config.json")
        sys.exit(1)

    # =========================================================================
    # PASO 3. Cargar matriz intrínseca K desde el archivo .npz
    # El archivo fué generado por calibrar_camara.py y contiene
    # la matriz K y los coeficientes de distorsión de la cámara
    # =========================================================================
    try:
        calibracion = np.load(args.calibracion)
        matriz_k = calibracion["matriz_k"]

    except FileNotFoundError:
        print(f"Error: no se encontró el archivo '{args.calibracion}'.")
        print("Ejecuta primero calibrar_camara.py para generarlo.")
        return

    # =========================================================================
    # PASO 4. Extraer distancia focal f de la matriz K
    # La matriz K tiene esta forma:
    #       [[fx, 0, cx],
    #         [0,fy, cy],
    #         [0, 0,  1]]
    # Usamos fx (posicion [0,0]) como distancia focal horizontal,
    # ya que mediremos el ancho del objeto en píxeles horizontales.
    # =========================================================================
    focal = float(matriz_k[0, 0])
    print(f"Calibración cargada desde '{args.calibracion}'")
    print(f"Distancia focal f(x): {focal:.2f} píxeles")

    # =========================================================================
    # PASO 5. Definir los rangos HSV para el color seleccionado
    # Reutilizamos los mismos rangos que en detector_color.py
    # =========================================================================
    rangos_hsv = {
        "rojo": (np.array([0, 120, 70]), np.array([10, 255, 255])),
        "verde": (np.array([36, 100, 100]), np.array([86, 255, 255])),
        "azul": (np.array([100, 150, 50]), np.array([140, 255, 255])),
        "amarillo": (np.array([20, 100, 100]), np.array([35, 255, 255])),
    }
    limite_inferior, limite_superior = rangos_hsv[args.color]

    # =========================================================================
    # PASO 6. Crear CameraClient y conectar con la Raspberry Pi
    # =========================================================================
    with CameraClient(
        host=args.host,
        port=args.port,
        width=args.width,
        height=args.height,
        rotation=args.rotation,
    ) as cam:
        print(f"Conectado a la cámara en {args.host}:{args.port}")
        print(f"Detectando color: {args.color} | Ancho real: {args.ancho_real_cm} cm")
        print("Pulsa 'q' para salir")

        cv2.namedWindow("Medición de distancia", cv2.WINDOW_NORMAL)

        try:
            while True:
                frame = cam.get_frame()
                if frame is None:
                    print("Conexión perdida")
                    break

                # =========================================================
                # PASO 7.1. Convertir BGR -> HSV y crear máscara
                # Mismo procedimiento que en detector_color.py
                # =========================================================
                hsv = cv2.cvtColor(src=frame, code=cv2.COLOR_BGR2HSV)
                mascara = cv2.inRange(
                    src=hsv,
                    lowerb=limite_inferior,
                    upperb=limite_superior,
                )

                # =========================================================
                # PASO 7.2. Encontrar contornos en la máscara
                # findContours devuelve la lista de contornos.
                # Nos quedamos con el más grande (mayor área),
                # que corresponde con el objeto principal detectado.
                # =========================================================
                contornos, _ = cv2.findContours(
                    image=mascara,
                    mode=cv2.RETR_EXTERNAL,
                    method=cv2.CHAIN_APPROX_SIMPLE,
                )

                if contornos:
                    contorno_mayor = max(contornos, key=cv2.contourArea)

                    # =====================================================
                    # PASO 7.3. Medir ancho en píxeles con boundingRect
                    # boundingRect devuelve (x, y, ancho, alto) del
                    # rectángulo que envuelve el contorno detectado
                    # =====================================================
                    x, y, ancho_px, alto_px = cv2.boundingRect(contorno_mayor)

                    # =====================================================
                    # PASO 7.4. Calcular la distancia D = (W * f) / P
                    #   W = Ancho real en cm (args.ancho_real_cm)
                    #   f = Distancia focal en pixeles (focal)
                    #   P = Ancho del objeto en píxeles (ancho_px)
                    # =====================================================
                    if ancho_px > 0:
                        distancia = (args.ancho_real_cm * focal) / ancho_px

                        # =================================================
                        # PASO 7.5. Dibujar rectángulo y distancia
                        # Rectángulo verde alrededor del objeto y texto
                        #   con la distancia estimada en cm.
                        # =================================================
                        cv2.rectangle(
                            img=frame,
                            pt1=(x, y),
                            pt2=(x + ancho_px, y + alto_px),
                            color=(0, 255, 0),
                            thickness=2,
                        )
                        cv2.putText(
                            img=frame,
                            text=f"{distancia:.1f} cm",
                            org=(x, y - 10),
                            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                            fontScale=0.8,
                            color=(0, 255, 0),
                            thickness=2,
                        )

                    cv2.imshow("Medición de distancia", frame)

                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break

        except KeyboardInterrupt:
            print("\nDetención solicitada por usuario.")

        finally:
            # =================================================================
            # PASO 8. Cerrar ventanas al salir
            # =================================================================
            cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
