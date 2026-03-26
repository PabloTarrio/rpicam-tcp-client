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
import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rpicam_tcp_client import CameraClient
from config_loader import load_config


def main():
    """
    Función principal con configuración completa desde argumentos.

    Flujo del programa:
        1. Cargar config.kson (si existe)
        2. argparse con 12 parámetros opcionales
        3. Crear CameraClient pasando TODO al servidor
        4. Conectar → servidor aplica JSON recibido
        5. Bucle: get_frame() → rotar → escalar → mostrar
        6. Salir con 'q' + limpieza automática
    """
    # =========================================================================
    # PASO 1: Cargar configuración desde config.json (si existe)
    # =========================================================================
    cfg = load_config()
    cfg_conexion = cfg.get("conexion", {})
    cfg_camara = cfg.get("camara", {})
    
    # =========================================================================
    # PASO 2: Parsear 12 parámetros opcionales con argparse
    # =========================================================================
    parser = argparse.ArgumentParser(
        description="Muestra video configurado desde el cliente."
    )
    parser.add_argument(
        "--host",
        default=cfg_conexion.get("host"),
        help="IP Raspberry Pi",
        )
    parser.add_argument(
        "--port",
        type=int,
        default=cfg_conexion.get("port", 5001),
        help="Puerto TCP"
        )

    parser.add_argument(
        "--width",
        type=int,
        default=cfg_camara.get("width"),
        help="Ancho destino")
    parser.add_argument(
        "--height",
        type=int,
        default=cfg_camara.get("height"),
        help="Alto destino")
    parser.add_argument(
        "--jpeg_quality",
        type=int,
        default=cfg_camara.get("jpeg-quality"),
        help="JPEG 0-100",
        )
    parser.add_argument(
        "--brightness",
        type=float,
        default=cfg_camara.get("brightness"),
        help="-1.0 a 1.0",
        )
    parser.add_argument(
        "--contrast",
        type=float,
        default=cfg_camara.get("contrast"),
        help="0.0-32.0")
    parser.add_argument(
        "--saturation",
        type=float,
        default=cfg_camara.get("saturation"),
        help="0.0-32.0")
    parser.add_argument(
        "--sharpness",
        type=float,
        default=cfg_camara.get("sharpness"),
        help="0.0-16.0")
    parser.add_argument(
        "--exposure_time",
        type=int,
        default=cfg_camara.get("exposure_time"),
        help="µs 114-694267")
    parser.add_argument(
        "--analogue_gain",
        type=float,
        default=cfg_camara.get("analogue_gain"),
        help="1.0-16.0")

    # Parámetros CLIENTE (local)
    parser.add_argument(
        "--rotation",
        type=int,
        default=cfg_camara.get("rotation"),
        choices=[0, 90, 180, 270],
        help="Rotación grados",
    )

    args = parser.parse_args()

    if args.host is None:
        print("Error: indica --host o configura 'host en config.json")

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
    # PASO 3: Crear CameraClient con mezcla servidor+cliente
    # =========================================================================
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
    # PASO 4: Conectar — Servidor aplica JSON recibido
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
