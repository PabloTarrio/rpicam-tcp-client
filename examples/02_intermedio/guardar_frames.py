"""
EJEMPLO 6 - Secuencia numerada de frames (time-lapse / dataset)

Tutorial paso a paso para capturar secuencias de imágenes.

OBJETIVO:
    Capturar N frames consecutivos desde la Raspberry Pi Camera y guardarlos
    como secuencia numerada: frame_001.jpg,  frame_002.jpg, etc.
    Base para time-lapse, datasets de IA y análisis frame a frame

REQUISITOS PREVIOS:
    - Completar ejemplos anteriores
    - Entender bucles for y context manager
    - Conocer cv2.imwrite de ejemplo 3

CONCEPTOS CLAVE:
    - Bucle for finito: capturar exactamente N frames
    - Numeración con f"frame_{i:03d}.jpg" (001, 002, 003, ...)
    - path.exists() para evitar sobrescribir carpetas existentes
    - pathlib.Path para manejo robusto de archivos
    - Progreso con tqdm para bucles largos

CASOS DE USO:
    - Time-lapse: acelerar experimentos largos (ffmpeg -r 30)
    - Datasets vision artificial: entrenamiento redes neuronales
    - Análisis cuantitativo frame a frame (brillo, color promedio,...)
    - Trigger inteligente: grabar solo cuando hay movimiento
    - Comparación antes/después en experimentos

TIEMPO ESTIMADO: 15 minutos

DETENER: Automático tras N frames. Ctrl+C para cancelar.
"""

import argparse
import sys
from pathlib import Path

import cv2
from tqdm import tqdm

from rpicam_tcp_client import CameraClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config_loader import load_config


def main():
    """
    Función principal: Conecta, captura secuencia y desconecta.

    Flujo del programa (PASO A PASO):

    1. Parsear argumentos (--host, --frames, --output-dir)
    2. Validar/crear directorio de salida
    3. Context manager CameraClient
    4. Bucle for con tqdm: get_frame() -> guardar numerado
    5. Salida limpia automática
    """
    # =========================================================================
    # PASO 1: Cargar configuración desde config.json (si existe)
    # =========================================================================
    cfg = load_config()
    cfg_conexion = cfg.get("conexion", {})
    cfg_camara = cfg.get("camara", {})
    cfg_frames = cfg.get("frames", {})

    # ================================================================
    # PASO 2: argparse parámetros secuencia
    # ================================================================
    parser = argparse.ArgumentParser(
        description="Captura secuencia numerada de frames (time-lapse/dataset)"
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
        "--frames",
        "-n",
        type=int,
        default=cfg_frames.get("frames", 100),
        help="Número de frames a capturar (default 100)",
    )
    parser.add_argument(
        "--prefix",
        "-p",
        default=cfg_frames.get("prefix", "frame"),
        help="Prefijo de los archivos generados (default 'frame')",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        default=cfg_frames.get("output_dir", "frames"),
        help="Carpeta de destino (default 'frames')",
    )
    parser.add_argument(
        "--width", type=int, default=cfg_camara.get("width", 640), help="Ancho frame"
    )
    parser.add_argument(
        "--height", type=int, default=cfg_camara.get("height", 480), help="Alto frame"
    )
    parser.add_argument(
        "--rotation",
        type=int,
        default=cfg_camara.get("rotation", 0),
        choices=[0, 90, 180, 270],
        help="Grados de Rotación",
    )
    args = parser.parse_args()

    if args.host is None:
        print("Error: indica --host o configura 'host' en config.json")
        sys.exit(1)

    # ================================================================
    # PASO 2: validar/crear directorio de salida
    # ================================================================
    output_dir = Path(args.output_dir)
    if output_dir.exists():
        print(f"ADVERTENCIA: '{output_dir}' ya existe. Se SOBREESCRIBIRÁ")
    else:
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Creado directorio: {output_dir.absolute()}")

    # ================================================================
    # PASO 3: conectar camara
    # ================================================================
    cam = CameraClient(
        host=args.host,
        port=args.port,
        width=args.width,
        height=args.height,
        rotation=args.rotation,
    )

    with cam:
        print(f"Capturando {args.frames} frames...")
        print(f"Formato: {args.prefix}_001.jpg, {args.prefix}_002.jpg,...")

        # ================================================================
        # PASO 4: bucle for con tqdm
        # ================================================================
        for i in tqdm(range(args.frames), desc="Capturando"):
            frame = cam.get_frame()
            if frame is None:
                print("\nError: conexión perdida")
                break

            # Guardar frame numerado
            filename = output_dir / f"{args.prefix}_{i + 1:03d}.jpg"
            success = cv2.imwrite(str(filename), frame)
            if not success:
                print(f"Error guardando {filename}")
                break

        print(f"\nSecuencia completada: {output_dir.absolute()}")


"""
EJERCICIOS para practicar:

    1. Intervalo entre frames: Añade --intervalo (segundos entre capturas).
        Usa time.sleep(args.intervalo) dentro del bucle.
        Para que sirve capturar 1 frame cada 10 segundos

    2. Time-lapse con ffmpeg: Captura 300 frames y ensambla el video:
        ffmpeg -r 30 -i frames/frame_%03d.jpg timelapse.mp4
        Que duracion tiene el video resultante?

    3. Prefijo por experimento: Prueba --prefix experimento_A y
        --prefix experimento_B en distintas condiciones de iluminacion.
        Compara los resultados visualmente.

    4. Analisis brillo: Tras capturar la secuencia, calcula el brillo
        medio de cada frame con numpy:
        PISTA: brillo = np.mean(cv2.imread(f"frames/frame_{i:03d}.jpg"))

    5. Mostrar previsualizacion: Añade cv2.imshow() dentro del bucle
        para ver cada frame mientras se captura.
        PISTA: combina con cv2.waitKey(1).

    6. RETO AVANZADO: Combina con detectar_movimiento.py para capturar
        frames SOLO cuando hay movimiento.
        PISTA: crea el BackgroundSubtractor antes del bucle for y añade
        una condicion if movimiento_detectado antes de cv2.imwrite().
"""
if __name__ == "__main__":
    main()
