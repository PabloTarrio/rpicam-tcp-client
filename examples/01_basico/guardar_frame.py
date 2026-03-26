"""
=============================================================================
EJEMPLO 3 - Capturar y guardar una fotografía única
=============================================================================

OBJETIVO
    Capturar UN SOLO frame desde la Raspberry Pi Camera y guardarlo como JPG
    en el ordenador remoto. Perfecto para capturas puntuales sin vídeo continuo.

REQUISITOS PREVIOS
    - Haber completado ejemplo 1 (mostrar_video.py)
    - Servidor corriendo: `sudo systemctl status camara-tcp.service`
    - Entender el uso del context manager `with` de ejemplo 1
    - (Opcional) Copiar config.example.json -> config.json y editar tu IP

CONCEPTOS CLAVE
    - Uso MÍNIMO de CameraClient: un solo `get_frame()`
    - Context manager `with`: connect/disconnect automático
    - `cv2.imwrite()` para guardar JPGs
    - Escalado/rotación LOCALES en cliente (width/height/rotation)
    - Protocolo JSON: parámetros servidor (jpegquality, brightness...)

CASOS DE USO
    - Capturas puntuales para documentación/experimentos
    - Dataset building para visión artificial
    - Verificación rápida del sistema
    - Base para timelapse o burst photography
    - Debugging: comprobar efecto de parámetros servidor

TIEMPO ESTIMADO: 10 minutos

DETENER: Script se cierra automáticamente tras guardar la imagen.
=============================================================================
"""

import argparse
import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config_loader import load_config

from rpicam_tcp_client import CameraClient


def main():
    """
    Función principal: conecta → captura 1 frame → guarda JPG → desconecta.

    Flujo del programa (PASO A PASO):

    1. Cargar config.json (si existe)
    1. Parsear argumentos, sobreescriben config.json
    2. Validar ruta de salida (--output)
    3. Crear CameraClient con parámetros servidor/cliente
    4. Context manager `with`: connect() automático
    5. Capturar UN SOLO frame con `get_frame()`
    7. Guardar con `cv2.imwrite()`
    8. Salida limpia (disconnect() automático)
    """
    # =========================================================================
    # PASO 1: Cargar configuración desde config.json (si existe)
    # =========================================================================
    cfg = load_config()
    cfg_conexion = cfg.get("conexion", {})
    cfg_camara = cfg.get("camara", {})

    # =============================================================================
    # PASO 2: argparse con parámetros pedagógicos
    # =============================================================================
    parser = argparse.ArgumentParser(
        description="Captura UN frame de la Raspberry Pi y lo guarda como JPG."
    )
    parser.add_argument(
        "--host",
        default=cfg_conexion.get("host"),
        help="IP de la Raspberry Pi",
        )
    parser.add_argument(
        "--port",
        type=int,
        default=cfg_conexion.get("port", 5001),
        help="Puerto TCP",
        )
    parser.add_argument(
        "--output",
        "-o",
        default="captura_cam.jpg",
        help="Archivo JPG destino (por defecto: captura_cam.jpg)",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=cfg_camara.get("width"),
        help="Ancho destino (local)",
        )
    parser.add_argument(
        "--height",
        type=int,
        default=cfg_camara.get("height"),
        help="Alto destino (local)",
        )
    parser.add_argument(
        "--jpeg_quality",
        type=int,
        default=cfg_camara.get("jpeg_quality"),
        help="JPEG 0-100",
        )
    parser.add_argument(
        "--brightness",
        type=float,
        default=cfg_camara.get("brightness"),
        help="-1.0 a 1.0",
        )
    parser.add_argument(
        "--rotation",
        type=int,
        default=cfg_camara.get("rotation", 0),
        choices=[0, 90, 180, 270],
        help="Rotación LOCAL (grados)",
    )
    args = parser.parse_args()

    if args.host is None:
        print("Error: indica --host o configura 'host' en config.json")
        sys.exit(1)

    # =============================================================================
    # PASO 3: validar archivo destino
    # =============================================================================
    output_path = Path(args.output)
    if output_path.exists():
        print(f"ADVERTENCIA:'{output_path}' ya existe. Se SOBREESCRIBIRÁ.")

    # =============================================================================
    # PASO 4: conectar con context manager (automático)
    # =============================================================================
    print(f"Conectando a {args.host}:{args.port}...")
    cam = CameraClient(
        host=args.host,
        port=args.port,
        width=args.width,
        height=args.height,
        jpeg_quality=args.jpeg_quality,
        brightness=args.brightness,
        rotation=args.rotation,
    )

    # =============================================================================
    # PASO 5 y 6: Conectar y capturar un único frame
    # =============================================================================
    with cam:  # ← connect() automático, disconnect() al salir
        print("Conectado. Capturando frame...")
        frame = cam.get_frame()

        if frame is None:
            print("Error: No se recibió frame (¿servidor caído?).")
            sys.exit(1)

        # =============================================================================
        # PASO 7: verificar dimensiones (pedagógico)
        # =============================================================================
        h, w = frame.shape[:2]
        print(
            f"Frame: {w}x{h} px (rot={args.rotation}°, w={args.width}, h={args.height})"
        )

        # =============================================================================
        # PASO 8: guardar JPG
        # =============================================================================
        success = cv2.imwrite(str(output_path), frame)
        if success:
            print(f"Guardado: {output_path.absolute()}")
        else:
            print("Error al guardar.")
            sys.exit(1)


# =============================================================================
# EJERCICIOS PARA PRACTICAR:
# =============================================================================
# 1. **Captura comparativa**: Guarda 3 imágenes variando `--jpegquality` (30, 70, 95). 
#                             Compara tamaños de archivo vs. calidad visual.
# 2. **Escalado y rotación**: Captura una imagen con:
#                             --width 640 --height 480 --rotation 90`.
#                             Verifica dimensiones y orientación en visor.
# 3. **Preset laboratorio**:  Encuentra valores óptimos para:
#                           ` --brightness` y `--saturation` para tu iluminación.
#                             Documenta en `config_lab.json`.
# 4. **Timelapse básico**:    Modifica para capturar 10 frames con:
#                  `          --output frame_{i:03d}.jpg`. Crea GIF con `ffmpeg`.
# 5. **Dataset visión**:      Captura 50 imágenes variando parámetros. 
#                             Organiza en carpetas por clase 
#                             (bien_iluminado, bajo_brillo).

if __name__ == "__main__":
    main()
