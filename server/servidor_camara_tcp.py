#!/usr/bin/env python3
"""
Servidor TCP para la Raspberry Pi Camera Module 2 NoIR.

Este script se ejecuta en la Raspberry Pi y hace tres cosas:
  1. Abre la cámara usando la librería 'picamera2'.
  2. Captura frames (fotogramas) continuamente.
  3. Los comprime en formato JPEG y los envía por TCP al cliente remoto.

Protocolo de envío (igual que en el servidor del LIDAR):
  - Primero se envían 4 bytes indicando el tamaño del frame en bytes.
  - Después se envían los bytes del frame comprimido.
  El cliente sabe así exactamente cuántos bytes debe leer.

NOTA: En Ubuntu 24.04 Server, el módulo 'pykms' no está disponible porque
es exclusivo de Raspberry Pi OS. Como nuestro servidor no necesita ninguna
previsualización gráfica, lo simulamos con MagicMock para que picamera2
pueda importarse sin errores.
"""

# MagicMock nos permite crear un objeto "falso" que imita cualquier módulo.
# Lo usamos para engañar a picamera2 y que no falle al buscar 'pykms'.
import sys
from unittest.mock import MagicMock

sys.modules["pykms"] = MagicMock()

import socket  # noqa: E402
import struct  # noqa: E402

import cv2  # noqa: E402
from picamera2 import Picamera2  # noqa: E402

# --- Configuración ---
TCP_HOST = "0.0.0.0"  # Escucha en todas las interfaces de red de la RPi
TCP_PORT = 5001  # Puerto 5001 para no colisionar con el LIDAR (puerto 5000)
FRAME_WIDTH = 640  # Ancho del frame en píxeles
FRAME_HEIGHT = 480  # Alto del frame en píxeles
JPEG_QUALITY = 80  # Calidad JPEG (0-100). Mayor = más calidad pero más peso


def configurar_camara():
    """
    Crea y configura la cámara con la resolución deseada.

    Usamos el modo 'still' (foto) en lugar de 'video' porque nos da
    imágenes de mayor calidad. La resolución se ajusta a FRAME_WIDTH x
    FRAME_HEIGHT definidos arriba.

    Returns:
        Picamera2: El objeto de la cámara ya configurado y arrancado.
    """
    cam = Picamera2()

    # Creamos una configuración de tipo 'still' (captura de imagen)
    # con el tamaño que hemos definido en la configuración
    config = cam.create_still_configuration(main={"size": (FRAME_WIDTH, FRAME_HEIGHT)})
    cam.configure(config)

    # Arrancamos la cámara: a partir de aquí ya está capturando
    cam.start()
    return cam


def enviar_frame(cliente, frame):
    """
    Comprime un frame a JPEG y lo envía al cliente por TCP.

    El protocolo de envío es:
      1. Empaquetamos el tamaño del frame en 4 bytes (un entero 'Long')
      2. Enviamos esos 4 bytes primero (el cliente sabrá cuánto leer)
      3. Enviamos los bytes del frame comprimido

    Args:
        cliente: El socket del cliente conectado.
        frame:   El frame capturado por la cámara (array de numpy).

    Returns:
        bool: True si el envío fue correcto, False si hubo un error.
    """
    # Comprimimos el frame a formato JPEG para reducir su tamaño
    # encode devuelve (éxito, array_de_bytes)
    resultado, buffer = cv2.imencode(
        ".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY]
    )

    if not resultado:
        print("Error al comprimir el frame a JPEG")
        return False

    # Convertimos el array de bytes a un objeto bytes de Python
    datos = buffer.tobytes()
    tamaño = len(datos)

    try:
        # Enviamos primero el tamaño en 4 bytes para que el cliente
        # sepa exactamente cuántos bytes debe leer a continuación
        cliente.sendall(struct.pack("L", tamaño))

        # Enviamos los bytes del frame comprimido
        cliente.sendall(datos)
        return True

    except (BrokenPipeError, ConnectionResetError):
        # El cliente se ha desconectado durante el envío
        return False


def main():
    """
    Función principal del servidor.

    Arranca la cámara, crea el socket TCP y entra en un bucle infinito
    esperando clientes. Cuando uno se conecta, le envía frames
    continuamente hasta que se desconecta, y entonces vuelve a esperar
    al siguiente cliente.
    """
    print("=" * 60)
    print("SERVIDOR CÁMARA TCP")
    print("=" * 60)

    # --- Paso 1: Arrancar la cámara ---
    print("[1] Iniciando la cámara...")
    cam = configurar_camara()
    print(f"    Cámara lista: {FRAME_WIDTH}x{FRAME_HEIGHT} px")

    # --- Paso 2: Crear el socket TCP del servidor ---
    print("[2] Iniciando servidor TCP...")
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # SO_REUSEADDR permite reutilizar el puerto inmediatamente después
    # de reiniciar el servidor, sin esperar el timeout del sistema
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((TCP_HOST, TCP_PORT))
    servidor.listen(1)  # Solo aceptamos 1 cliente a la vez
    print(f"    Escuchando en puerto {TCP_PORT}")

    try:
        while True:
            # --- Paso 3: Esperar a que un cliente se conecte ---
            print("[3] Esperando cliente...")
            cliente, direccion = servidor.accept()
            print(f"    Cliente conectado desde {direccion}")

            frame_count = 0
            try:
                # --- Paso 4: Enviar frames continuamente ---
                while True:
                    # Capturamos un frame de la cámara como array de numpy
                    frame = cam.capture_array()

                    # Intentamos enviarlo al cliente
                    if not enviar_frame(cliente, frame):
                        # Si falla el envío, el cliente se ha desconectado
                        break

                    frame_count += 1
                    print(f"    Frame {frame_count} enviado", end="\r")

            except Exception as e:
                print(f"\n    Error durante el streaming: {e}")
            finally:
                # Cerramos la conexión con este cliente antes de
                # volver a esperar al siguiente
                cliente.close()
                print(f"\n    Cliente desconectado tras {frame_count} frames")

    except KeyboardInterrupt:
        # El usuario ha pulsado Ctrl+C para detener el servidor
        print("\n\nInterrupción detectada. Deteniendo servidor...")
    finally:
        # Siempre cerramos la cámara y el socket, pase lo que pase
        servidor.close()
        cam.stop()
        cam.close()
        print("=" * 60)
        print("Servidor cerrado correctamente")
        print("=" * 60)


# Este bloque garantiza que main() solo se ejecuta cuando lanzamos
# el script directamente (no cuando se importa como módulo)
if __name__ == "__main__":
    main()
