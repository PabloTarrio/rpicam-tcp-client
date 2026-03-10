"""
Ejemplo básico: mostrar vídeo en tiempo real desde la Raspberry Pi.

Demuestra el uso más sencillo de CameraClient: conectarse al servidor,
recibir frames continuamente y mostrarlos en pantalla con OpenCV.

En este ejemplo se usan los valores por defecto del servidor para todos
los parámetros de la cámara (resolución, calidad JPEG, etc.).

Uso:
    python mostrar_video.py --host <IP_RASPBERRY>
    python mostrar_video.py --host <IP_RASPBERRY> --port 5001

Controles:
    Q  →  salir
"""

import argparse

import cv2

from rpicam_tcp_client import CameraClient


def main():
    parser = argparse.ArgumentParser(description="Muestra vídeo desde la Raspberry Pi.")
    parser.add_argument("--host", required=True, help="IP de la Raspberry Pi")
    parser.add_argument(
        "--port", type=int, default=5001, help="Puerto TCP (por defecto 5001)"
    )
    args = parser.parse_args()

    msg = f"Conectando a {args.host}:{args.port}. Valores por defecto del servidor."
    print(msg)

    with CameraClient(host=args.host, port=args.port) as cam:
        print("Recibiendo vídeo. Pulsa Q para salir.")
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
