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

from rpicam_tcp_client import CameraClient


def main():
    """
    Función principal: conecta → captura 1 frame → guarda JPG → desconecta.

    Flujo del programa (PASO A PASO):

    1. Parsear argumentos (--host obligatorio, resto opcionales)
    2. Validar ruta de salida (--output)
    3. Crear CameraClient con parámetros servidor/cliente
    4. Context manager `with`: connect() automático
    5. Capturar UN SOLO frame con `get_frame()`
    6. Verificar dimensiones (confirmar escalado/rotación)
    7. Guardar con `cv2.imwrite()`
    8. Salida limpia (disconnect() automático)
    """
    # =============================================================================
    # PASO 1: argparse con parámetros pedagógicos
    # =============================================================================
    parser = argparse.ArgumentParser(
        description="Captura UN frame de la Raspberry Pi y lo guarda como JPG."
    )
    parser.add_argument("--host", required=True, help="IP de la Raspberry Pi")
    parser.add_argument("--port", type=int, default=5001, help="Puerto TCP")
    parser.add_argument(
        "--output",
        "-o",
        default="captura_cam.jpg",
        help="Archivo JPG destino (por defecto: captura_cam.jpg)",
    )
    parser.add_argument("--width", type=int, default=None, help="Ancho destino (local)")
    parser.add_argument("--height", type=int, default=None, help="Alto destino (local)")
    parser.add_argument("--jpegquality", type=int, default=None, help="JPEG 0-100")
    parser.add_argument("--brightness", type=float, default=None, help="-1.0 a 1.0")
    parser.add_argument(
        "--rotation",
        type=int,
        default=0,
        choices=[0, 90, 180, 270],
        help="Rotación LOCAL (grados)",
    )
    args = parser.parse_args()

    # =============================================================================
    # PASO 2: validar archivo destino
    # =============================================================================
    output_path = Path(args.output)
    if output_path.exists():
        print(f"ADVERTENCIA:'{output_path}' ya existe. Se SOBREESCRIBIRÁ.")

    # =============================================================================
    # PASO 3: conectar con context manager (automático)
    # =============================================================================
    print(f"Conectando a {args.host}:{args.port}...")
    cam = CameraClient(
        host=args.host,
        port=args.port,
        width=args.width,
        height=args.height,
        jpegquality=args.jpegquality,
        brightness=args.brightness,
        rotation=args.rotation,
    )

    with cam:  # ← connect() automático, disconnect() al salir
        print("Conectado. Capturando frame...")

        # =============================================================================
        # PASO 4: UN SOLO get_frame() (sin bucle)
        # =============================================================================
        frame = cam.get_frame()
        if frame is None:
            print("Error: No se recibió frame (¿servidor caído?).")
            sys.exit(1)

        # =============================================================================
        # PASO 5: verificar dimensiones (pedagógico)
        # =============================================================================
        h, w = frame.shape[:2]
        print(
            f"Frame: {w}x{h} px (rot={args.rotation}°, w={args.width}, h={args.height})"
        )

        # =============================================================================
        # PASO 6: guardar JPG
        # =============================================================================
        success = cv2.imwrite(str(output_path), frame)
        if success:
            print(f"Guardado: {output_path.absolute()}")
        else:
            print("Error al guardar.")
            sys.exit(1)


"""
# =============================================================================
## EJERCICIOS PARA PRACTICAR:
# =============================================================================

1. **Captura comparativa**: Guarda 3 imágenes variando `--jpegquality` (30, 70, 95). 
        Compara tamaños de archivo vs. calidad visual.

2. **Escalado y rotación**: Captura una imagen con:
                                     `--width 640 --height 480 --rotation 90`.
        Verifica dimensiones y orientación en visor.

3. **Preset laboratorio**: Encuentra valores óptimos de `--brightness` y `--saturation` 
        para tu iluminación. Documenta en `config_lab.json`.

4. **Timelapse básico**: Modifica para capturar 10 frames con:
                 `--output frame_{i:03d}.jpg`. Crea GIF con `ffmpeg`.

5. **Dataset visión**: Captura 50 imágenes variando parámetros. 
        Organiza en carpetas por clase (bien_iluminado, bajo_brillo).
"""

if __name__ == "__main__":
    main()
