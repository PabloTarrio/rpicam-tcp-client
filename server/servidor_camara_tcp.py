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
import json
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
FRAME_WIDTH = 1920  # Ancho del frame en píxeles
FRAME_HEIGHT = 1080  # Alto del frame en píxeles
JPEG_QUALITY = 80  # Calidad JPEG (0-100). Mayor = más calidad pero más peso


def recibir_parametros(cliente) -> dict:
    """
    Lee el JSON de configuración que envía el cliente al conectarse.

    El cliente envía primero 4 bytes con el tamaño del JSON, y después
    los bytes del JSON en sí. Este es el mismo protocolo que usamos
    para enviar frames, pero en dirección contraria.

    Si ocurre cualquier error al leer, devuelve un diccionario vacío
    y el servidor usará sus valores por defecto para todo.

    Args:
        cliente: El socket del cliente recién conectado.

    Returns:
        dict: Los parámetros enviados por el cliente, o {} si hubo error.
    """
    try:
        # 1. Leer los 4 bytes que indican el tamaño del JSON
        payload_size = struct.calcsize("L")
        data = b""
        while len(data) < payload_size:
            packet = cliente.recv(payload_size - len(data))
            if not packet:
                return {}
            data += packet

        # 2. Extraer el tamaño y leer exactamente esos bytes
        msg_size = struct.unpack("L", data)[0]
        json_data = b""
        while len(json_data) < msg_size:
            packet = cliente.recv(min(msg_size - len(json_data), 4096))
            if not packet:
                return {}
            json_data += packet

        # 3. Decodificar el JSON a un diccionario Python
        params = json.loads(json_data.decode("utf-8"))
        print(f"  Parámetros recibidos del cliente: {params}")
        return params

    except Exception as e:
        msg = f"  Error al leer parámetros del cliente: {e}. Valores por defecto."
        print(msg)
        return {}


def configurar_camara(params: dict):
    """
    Crea y configura la cámara aplicando los parámetros recibidos del cliente.

    Los valores del cliente sobreescriben los valores por defecto definidos
    en las constantes de configuración. Si el cliente no especificó algún
    parámetro, se usa el valor por defecto del servidor.

    Args:
        params (dict): Parámetros enviados por el cliente. Puede estar vacío.

    Returns:
        Picamera2: El objeto de la cámara ya configurado y arrancado.
    """
    # Fusionamos los valores por defecto con los del cliente.
    # Los del cliente tienen prioridad si están presentes.
    width = params.get("width", FRAME_WIDTH)
    height = params.get("height", FRAME_HEIGHT)
    jpeg_quality = params.get("jpeg_quality", JPEG_QUALITY)

    cam = Picamera2()

    config = cam.create_still_configuration(main={"size": (width, height)})
    cam.configure(config)

    # Aplicamos los controles de imagen si el cliente los especificó
    controles = {}
    if "brightness" in params:
        controles["Brightness"] = params["brightness"]
    if "contrast" in params:
        controles["Contrast"] = params["contrast"]
    if "saturation" in params:
        controles["Saturation"] = params["saturation"]
    if "sharpness" in params:
        controles["Sharpness"] = params["sharpness"]
    if "exposure_time" in params:
        controles["ExposureTime"] = params["exposure_time"]
    if "analogue_gain" in params:
        controles["AnalogueGain"] = params["analogue_gain"]

    if controles:
        cam.set_controls(controles)

    cam.start()
    return cam, width, height, jpeg_quality


def enviar_frame(cliente, frame, jpeg_quality: int):
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
        ".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality]
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
            print(f"  Cliente conectado desde {direccion}")

            # Leer parámetros y configurar la cámara
            params = recibir_parametros(cliente)
            cam, width, height, jpeg_quality = configurar_camara(params)
            print(f"  Cámara lista: {width}x{height} px, JPEG quality: {jpeg_quality}")

            frame_count = 0
            try:
                # --- Paso 4: Enviar frames continuamente ---
                while True:
                    # Capturamos un frame de la cámara como array de numpy
                    frame = cam.capture_array()

                    # Intentamos enviarlo al cliente
                    if not enviar_frame(cliente, frame, jpeg_quality):
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
                cam.stop()
                cam.close()
                print(f"\n    Cliente desconectado tras {frame_count} frames")

    except KeyboardInterrupt:
        # El usuario ha pulsado Ctrl+C para detener el servidor
        print("\n\nInterrupción detectada. Deteniendo servidor...")
    finally:
        # Siempre cerramos la cámara y el socket, pase lo que pase
        servidor.close()
        print("=" * 60)
        print("Servidor cerrado correctamente")
        print("=" * 60)


# Este bloque garantiza que main() solo se ejecuta cuando lanzamos
# el script directamente (no cuando se importa como módulo)
if __name__ == "__main__":
    main()
