"""
EJEMPLO 4 - Grabar video MP4 con timestamps

Tutorial paso a paso para grabación de video continuo

OBJETIVO:
    Grabar vídeo desde Raspberry Pi Camera en formato MP4 (H.264) con
    timestamp superpuesto. Duración configurable.

REQUISITOS PREVIOS:
    - Completar ejemplos 1-3 (mostrar_video.py, guardar_frame.py)
    - Entender bucles infinitos y context managers
    - Conocer `cv2.VideoWriter`

CONCEPTOS CLAVE:
    - `cv2.VideoWriter`: codec H.264 para MP4
    - Timestamp superpuesto (`cv2.putText`)
    - FPS configurable para grabación estable
    - Duración limitada por frames o por tiempo
    - `datetime` para marcas temporales

CASOS DE USO
    - Documentación de experimentos
    - Análisis post-procesado (vision artificial)
    - Grabación evidencia para informes
    - Time-lapse acelerado
    - Streaming -> archivo local

TIEMPO ESTIMADO:
    - 15 minutos

DETENER:
    - Pulsa `q` o llega al límite configurado
"""

import argparse
import time
from datetime import datetime

import cv2

from rpicam_tcp_client import CameraClient


def main():
    """
    Función principal: conecta - graba MP4 - desconecta

    Flujo de programa (PASO A PASO):

    1. Parsear argumentos (duración, FPS, output)
    2. Calcular frames_total = duration * fps
    3. Configurar VideoWriter (H.264 codec)
    4. Context manager CameraClient
    5. Bucle grabación: frame -> timestamp -> write()
    6. Liberar writer y salir limpio
    """
    # ===============================================================
    # PASO 1: argparse parámetros grabación
    # ===============================================================
    parser = argparse.ArgumentParser(
        description="Graba video MP4 desde Raspberry Pi Camera."
    )

    parser.add_argument("--host", required=True, help="IP Raspberry Pi")
    parser.add_argument("--port", type=int, default=5001, help="Puerto TCP")
    parser.add_argument(
        "--output", "-o", default="video.mp4", help="Archivo MP4 destino"
    )
    parser.add_argument(
        "--duration", "-d", type=int, default=30, help="Duración segundos (default 30)"
    )
    parser.add_argument(
        "--fps", type=int, default=15, help="FPS grabación (default 15)"
    )
    parser.add_argument("--width", type=int, default=640, help="Ancho frame")
    parser.add_argument("--height", type=int, default=480, help="Alto frame")
    parser.add_argument(
        "--rotation",
        type=int,
        default=0,
        choices=[0, 90, 180, 270],
        help="Grados de Rotación",
    )
    args = parser.parse_args()

    # ===============================================================
    # PASO 2: calcular los frames totales
    # ===============================================================
    frames_total = args.duration * args.fps
    print(f"Grabando {args.duration}s a {args.fps}FPS = {frames_total} frames")
    print(f"Output: {args.output} ({args.width}x{args.height})")

    # ===============================================================
    # PASO 3: Videowriter H.264
    # ===============================================================
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # Codec H.264
    out = cv2.VideoWriter(
        filename=args.output,
        fourcc= fourcc,
        fps= args.fps,
        frameSize=(args.width, args.height),
        )

    # ===============================================================
    # PASO 4: Conectar Camara
    # ===============================================================
    cam = CameraClient(
        host=args.host,
        port=args.port,
        width=args.width,
        height=args.height,
        rotation=args.rotation,
    )

    with cam:
        print("Grabación iniciada. Pulsa 'q' para parar.")
        cv2.namedWindow("Grabando...", cv2.WINDOW_NORMAL)
        frame_count = 0
        frame_time = 1.0 / args.fps

        while frame_count < frames_total:
            frame_start = time.time()

            # ===============================================================
            # PASO 5: Capturar frame
            # ===============================================================
            frame = cam.get_frame()
            if frame is None:
                print("Conexión perdida")
                break

            # ===============================================================
            # PASO 6: Añadir TIMESTAMP
            # ===============================================================
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            cv2.putText(
                img=frame,
                text=timestamp,
                org=(10, 30),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.7,
                color=(0, 255, 0),
                thickness=2,
            )

            # ===============================================================
            # PASO 7: Grabar y mostrar
            # ===============================================================
            out.write(frame)
            cv2.imshow("Grabando...", frame)
            frame_count += 1

            # Control FPS real
            elapsed = time.time() - frame_start
            sleep_time = max(0, frame_time - elapsed)
            time.sleep(sleep_time)

            # Mostrar porcentaje de progreso en la grabación
            progress = (frame_count / frames_total) * 100
            print(f"\rProgreso: {progress:.1f}% ({frame_count}/{frames_total})", end="")

            # Controles de la grabación ('q'= fin)
            if cv2.waitKey(delay=1) & 0xFF == ord("q"):
                break

        print("\nGrabación finalizada.")

    # ===============================================================
    # PASO 7: Liberar recurso
    # ===============================================================
    out.release()
    cv2.destroyAllWindows()
    print(f"Video guardado: {args.output}")

# =============================================================================
# EJERCICIOS PARA PRACTICAR:
# =============================================================================
# 1. Sin timestamp: Elimina cv2.putText y compara tamaño archivo.
#    Cuanto pesa el texto en bytes?
# 2. Cambiar color timestamp: Sustituye (0, 255, 0) por (0, 0, 255)
#    (rojo) o (255, 255, 255) (blanco). Cual se lee mejor?
# 3. FPS variable: Prueba --fps 5, --fps 15, --fps 30.
#    Observa diferencia fluidez vs tamaño archivo.
# 4. Resolucion: Prueba --width 1280 --height 720.
#    Cuanto tarda mas en grabar? Por que?
# 5. Nombre automatico: Modifica --output para que por defecto
#    sea video_YYYYMMDD_HHMMSS.mp4 usando datetime.now().
# 6. RETO FPS REAL: Ejecuta el script y mide cuanto tarda
#    realmente la grabacion de 10 segundos con un cronometro.
#    - Por que la grabacion dura mas que el video resultante?
#    - Cuantos frames por segundo envia realmente la camara por TCP?
#    - Como modificarias el codigo para que VideoWriter use el FPS
#      real de la red en lugar del FPS configurado?
#    PISTA: mide time.time() antes y despues de 10 frames
#    consecutivos con get_frame().
# =============================================================================

if __name__ == "__main__":
    main()
