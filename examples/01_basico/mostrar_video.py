"""
Ejemplo básico: recibir y mostrar video desde la Raspberry Pi Camera.

Este script se conecta al servidor TCP que corre en la Raspberry Pi,
recibe frames continuamente y los muestra en una ventana en la pantalla.

Uso:

    python3 mostrar_video.py

Controles:

    - Usa 'q' para salir

Requisitos:

    - El servidor servidor_camara_tcp.py debe estar corriendo en la RPi.
    - Ajusta HOST con la IP de tu Raspberry Pi.
"""

from rpicam_tcp_client import CameraClient

# --- Configuración ---
HOST = "172.16.125.90"
PORT = 5001


def main():
    print("Conectado al servidor de la cámara...")
    print(f"   Host: {HOST}:{PORT}")
    print("Pulsa 'q' para salir\n")

    with CameraClient(HOST, PORT) as cam:
        frame_count = 0

        while True:
            # Recibimos un frame del servidor
            frame = cam.get_frame()

            if frame is None:
                print("No se pudo recibir el frame. Saliendo....")
                break

            frame_count += 1
            print(f"Frame {frame_count} recibido", end="\r")

            # Mostramos el frame en una ventana
            import cv2

            cv2.imshow("Raspberry Pi Camera", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                print("\nSaliendo...")
                break

    # Cerramos todas las ventanas de OpenCV
    import cv2

    cv2.destroyAllWindows()
    print(f"Total de frames recibidos: {frame_count}")


if __name__ == "__main__":
    main()
