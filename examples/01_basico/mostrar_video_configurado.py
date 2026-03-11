"""
Ejemplo básico: mostrar vídeo con parámetros de cámara personalizados.

Demuestra cómo configurar la cámara desde el cliente: resolución,
calidad JPEG y ajustes de imagen (brillo, contraste, saturación, etc.).

El cliente envía los parámetros al servidor al conectarse. El servidor
los aplica sobre sus valores por defecto y empieza a enviar frames.

Uso:
    python mostrar_video_configurado.py --host <IP_RASPBERRY>
    python mostrar_video_configurado.py --host <IP_RASPBERRY> --width 640 --height 480
    python mostrar_video_configurado.py --host <IP_RASPBERRY> --saturation 0.5

Controles:
    Q  →  salir
"""

import argparse

import cv2

from rpicam_tcp_client import CameraClient


def main():
    parser = argparse.ArgumentParser(
        description="Muestra video desde la Raspberry Pi con parámetrosconfigurables."
    )

    parser.add_argument("--host", required=True, help="IP de la Raspberry Pi")
    parser.add_argument("--port", type=int, default=5001, help="Puerto TCP")
    parser.add_argument("--width", type=int, default=None, help="Ancho del frame")
    parser.add_argument("--height", type=int, default=None, help="Alto del frame")
    parser.add_argument(
        "--jpeg-quality", type=int, default=None, help="Calidad JPEG (0-100)"
    )
    parser.add_argument("--brightness", type=float, default=None, help="Brillo")
    parser.add_argument("--contrast", type=float, default=None, help="Contraste")
    parser.add_argument("--saturation", type=float, default=None, help="Saturación")
    parser.add_argument("--sharpness", type=float, default=None, help="Nitidez")
    parser.add_argument(
        "--exposure-time", type=int, default=None, help="Tiempo de exposición (µs)"
    )
    parser.add_argument(
        "--analogue-gain", type=float, default=None, help="Ganancia analógica"
    )
    parser.add_argument(
        "--rotation",
        type=int,
        default=0,
        choices=[0, 90, 180, 270],
        help="Rotación de la imagen en grados (0, 90, 180, 270)",
    )
    args = parser.parse_args()

    cam = CameraClient(
        host=args.host,
        port=args.port,
        width=args.width,
        height=args.height,
        jpeg_quality=args.jpeg_quality,
        brightness=args.brightness,
        contrast=args.contrast,
        saturation=args.saturation,
        sharpness=args.sharpness,
        exposure_time=args.exposure_time,
        analogue_gain=args.analogue_gain,
        rotation=args.rotation,
    )

    with cam:
        print("Recibiendo video. Pulse q para salir.")
        while True:
            frame = cam.get_frame()
            if frame is None:
                print("Conexión perdida.")
                break

            cv2.imshow("Raspberry Pi Camera", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
