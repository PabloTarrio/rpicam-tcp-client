#!/usr/bin/env python3
"""
=============================================================================
EJEMPLO 2: Video Configurado — Control total desde el cliente
=============================================================================

OBJETIVO:
    Personalizar completamente la cámara desde el cliente: resolución,
    calidad JPEG, controles de imagen (brillo, contraste, saturación) y
    rotación local.

REQUISITOS PREVIOS:
    - Haber completado ejemplo 1 (mostrar_video.py)
    - Entender el protocolo JSON cliente→servidor
    - Conocer que width/height se escalan LOCALMENTE (cv2.resize)

CONCEPTOS CLAVE:
    - Protocolo JSON: cliente envía parámetros al conectarse
    - Escalado local: servidor envía 1920x1080, cliente redimensiona
    - Controles picamera2: brightness, contrast, saturation, etc.
    - argparse completo con 12 parámetros opcionales

CASOS DE USO:
    - Adaptar resolución a ancho de banda disponible
    - Corregir orientación física de la cámara
    - Optimizar calidad JPEG para streaming
    - Experimentos de visión artificial
    - Aplicaciones embebidas con recursos limitados

TIEMPO ESTIMADO: 20 minutos

DETENER: Pulsa `q` en la ventana para salir
=============================================================================
"""

import argparse

import cv2

from rpicam_tcp_client import CameraClient


def main():
    """
    Función principal con configuración completa desde argumentos.

    Flujo del programa:
        1. argparse con 12 parámetros opcionales
        2. Crear CameraClient pasando TODO al servidor
        3. Conectar → servidor aplica JSON recibido
        4. Bucle: get_frame() → rotar → escalar → mostrar
        5. Salir con 'q' + limpieza automática
    """

    # =========================================================================
    # PASO 1: Parsear 12 parámetros opcionales con argparse
    # =========================================================================
    # Cada parámetro se pasa a CameraClient si != None.
    # El servidor fusiona con sus valores por defecto.

    parser = argparse.ArgumentParser(
        description="Muestra video configurado desde el cliente."
    )
    parser.add_argument("--host", required=True, help="IP Raspberry Pi")
    parser.add_argument("--port", type=int, default=5001, help="Puerto TCP")

    # Parámetros SERVIDOR (JSON)
    parser.add_argument("--width", type=int, default=None, help="Ancho destino")
    parser.add_argument("--height", type=int, default=None, help="Alto destino")
    parser.add_argument("--jpeg_quality", type=int, default=None, help="JPEG 0-100")
    parser.add_argument("--brightness", type=float, default=None, help="-1.0 a 1.0")
    parser.add_argument("--contrast", type=float, default=None, help="0.0-32.0")
    parser.add_argument("--saturation", type=float, default=None, help="0.0-32.0")
    parser.add_argument("--sharpness", type=float, default=None, help="0.0-16.0")
    parser.add_argument("--exposure_time", type=int, default=None, help="µs 114-694267")
    parser.add_argument("--analogue_gain", type=float, default=None, help="1.0-16.0")

    # Parámetros CLIENTE (local)
    parser.add_argument(
        "--rotation",
        type=int,
        default=0,
        choices=[0, 90, 180, 270],
        help="Rotación grados",
    )

    args = parser.parse_args()

    # Mostrar parámetros que se enviarán
    params_servidor = {
        k: v
        for k, v in vars(args).items()
        if k
        in [
            "width",
            "height",
            "jpeg_quality",
            "brightness",
            "contrast",
            "saturation",
            "sharpness",
            "exposure_time",
            "analogue_gain",
        ]
        and v is not None
    }
    print(f"Parámetros SERVIDOR: {params_servidor}")

    # =========================================================================
    # PASO 2: Crear CameraClient con mezcla servidor+cliente
    # =========================================================================
    # 9 parámetros → JSON al servidor
    # 3 parámetros → procesados localmente (width/height/rotation)

    cam = CameraClient(
        host=args.host,
        port=args.port,
        # SERVIDOR (JSON)
        width=args.width,
        height=args.height,
        jpeg_quality=args.jpeg_quality,
        brightness=args.brightness,
        contrast=args.contrast,
        saturation=args.saturation,
        sharpness=args.sharpness,
        exposure_time=args.exposure_time,
        analogue_gain=args.analogue_gain,
        # CLIENTE (local)
        rotation=args.rotation,
    )

    # =========================================================================
    # PASO 3: Conectar — Servidor aplica JSON recibido
    # =========================================================================
    # El servidor imprime: "Parámetros recibidos del cliente: {...}"
    # Configura picamera2 y empieza a enviar frames.

    with cam:
        print("Video configurado activo. Pulsa 'q' para salir.")

        # =====================================================================
        # PASO 4: Bucle principal con post-procesado local
        # =====================================================================

        while True:
            frame = cam.get_frame()
            if frame is None:
                print("Conexión perdida.")
                break

            # -----------------------------------------------------------------
            # 4.1: Rotación LOCAL (cv2.rotate)
            # -----------------------------------------------------------------
            # Se aplica EN la función get_frame(), por lo que no es necesario
            #       realizarlo aqui, aunque se pase como parámetro.

            # -----------------------------------------------------------------
            # 4.2: Escalado LOCAL (cv2.resize)
            # -----------------------------------------------------------------
            # Servidor SIEMPRE envía 1920x1080.
            # Cliente redimensiona a width/height solicitados.
            # Mantiene aspect ratio si solo se especifica uno.

            if args.width is not None or args.height is not None:
                h, w = frame.shape[:2]
                target_w = args.width if args.width else w
                target_h = args.height if args.height else h
                frame = cv2.resize(frame, (target_w, target_h))

            # -----------------------------------------------------------------
            # 4.3: Mostrar frame procesado
            # -----------------------------------------------------------------
            cv2.imshow("Raspberry Pi Camera Configurada", frame)

            # -----------------------------------------------------------------
            # 4.4: Salir con 'q'
            # -----------------------------------------------------------------
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cv2.destroyAllWindows()


# =============================================================================
# EJERCICIOS PARA PRACTICAR:
# =============================================================================
#
# 1. **BÁSICO**: Añade `--fps` para mostrar FPS cada 30 frames.
#
# 2. **INTERMEDIO**: Teclas `↑↓←→` para ajustar `brightness` en vivo.
#    Pista: Reconectar con nuevos parámetros.
#
# 3. **AVANZADO**: `--detect_faces` usando `cv2.CascadeClassifier`.
#    Dibuja rectángulos verdes alrededor de caras detectadas.
#
# 4. **INVESTIGACIÓN**: Compara FPS y latencia visual con/sin `--width 320`.
#
# 5. **OPTIMIZACIÓN**: Añade `--quality_auto` que ajuste JPEG según FPS.
#    Si FPS<15, baja calidad automáticamente.
#
# =============================================================================


if __name__ == "__main__":
    main()
