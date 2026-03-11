"""
Cliente TCP para conectarse al servidor de la Raspberry Pi Camera y recibir frames.
"""

import json
import socket
import struct

import cv2
import numpy as np


class CameraClient:
    """
    Cliente para recibir frames de video desde la Raspberry Pi a través de TCP.
    """

    def __init__(
        self,
        host: str,
        port: int = 5001,
        *,
        width: int | None = None,
        height: int | None = None,
        jpeg_quality: int | None = None,
        brightness: float | None = None,
        contrast: float | None = None,
        saturation: float | None = None,
        sharpness: float | None = None,
        exposure_time: int | None = None,
        analogue_gain: float | None = None,
        rotation: int = 0,
    ):
        """
        Inicializa el cliente.

        Args:
            host (str): Dirección IP de la Raspberry Pi.
            port (int): Puerto del servidor (por defecto 5001).
            width (int | None): Ancho destino del frame en píxeles. Se aplica
                localmente con cv2.resize. Si es None, no se escala.
            height (int | None): Alto destino del frame en píxeles. Se aplica
                localmente con cv2.resize. Si es None, no se escala.
            jpeg_quality (int | None): Calidad JPEG (0-100). Si es None, usa
                el valor por defecto del servidor.
            brightness (float | None): Brillo de la imagen. Si es None, usa
                el valor por defecto del servidor.
            contrast (float | None): Contraste de la imagen. Si es None, usa
                el valor por defecto del servidor.
            saturation (float | None): Saturación de la imagen. Si es None,
                usa el valor por defecto del servidor.
            sharpness (float | None): Nitidez de la imagen. Si es None, usa
                el valor por defecto del servidor.
            exposure_time (int | None): Tiempo de exposición en microsegundos.
                Si es None, usa el valor por defecto del servidor.
            analogue_gain (float | None): Ganancia analógica del sensor.
                Si es None, usa el valor por defecto del servidor.
            rotation (int): Rotación de la imagen en grados. Valores válidos:
                (0, 90, 180, 270). Por defecto 0, sin rotación.
        """
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False

        self._params: dict = {}
        self._width = width
        self._height = height
        if jpeg_quality is not None:
            self._params["jpeg_quality"] = jpeg_quality
        if brightness is not None:
            self._params["brightness"] = brightness
        if contrast is not None:
            self._params["contrast"] = contrast
        if saturation is not None:
            self._params["saturation"] = saturation
        if sharpness is not None:
            self._params["sharpness"] = sharpness
        if exposure_time is not None:
            self._params["exposure_time"] = exposure_time
        if analogue_gain is not None:
            self._params["analogue_gain"] = analogue_gain
        if rotation not in (0, 90, 180, 270):
            msg_rotation = "Rotación debe ser 0, 90, 180 o 270. Recibido:"
            raise ValueError(f"{msg_rotation}{rotation}")
        self._rotation = rotation

    def connect(self):
        """
        Conecta al servidor TCP de la cámara y envía los parámetros
        de configuración como JSON.

        El servidor leerá este JSON antes de empezar a enviar frames,
        y aplicará los parámetros recibidos sobre sus valores por defecto.
        Si no se especificó ningún parámetro, se envía un JSON vacío {}
        y el servidor usará toda su configuración por defecto.
        """
        if self.connected:
            raise Exception("Ya estás conectado al servidor")

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.connected = True
        print(f"Conectado a la cámara en {self.host}:{self.port}")

        # Serializamos los parámetros a JSON y los enviamos al servidor.
        # Si _params está vacío, enviamos {} y el servidor usará sus
        # valores por defecto para todo
        params_json = json.dumps(self._params).encode("utf-8")

        # Primero enviamos el tamaño del JSON en 4 bytes, igual que
        # hacemos con los frames. Así el servidor sabe cuantos bytes leer.
        self.socket.sendall(struct.pack("L", len(params_json)))
        self.socket.sendall(params_json)
        params_info = self._params if self._params else "ninguno (valores por defecto)"
        print(f"   Parámetros enviados: {params_info}")

    def disconnect(self):
        """
        Cierra la conexión con el servidor
        """
        if self.connected and self.socket:
            self.socket.close()
            self.connected = False
            print("Desconectado del servidor de la cámara")

    def __enter__(self):
        """
        Soporte para context manager 'with'.
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Cierra  automáticamente al salir del 'with'
        """
        self.disconnect()

    def get_frame(self):
        """
        Recibir un frame de video del servidor y lo decodifica.

        Returns:
            np.ndarray: La imagen decodificada lista para mostrar con OpenCV,
                        o None si hubo un error de conexión
        """
        if not self.connected or not self.socket:
            raise Exception("No hay conexión con el servidor")

        try:
            # 1. Recibir los 4 bytes del tamaño del frame (empaquetado como 'Long')
            payload_size = struct.calcsize("L")
            data = b""

            # Asegurarnos de recibir esos 4 bytes completos
            while len(data) < payload_size:
                packet = self.socket.recv(payload_size - len(data))
                if not packet:
                    return None  # El servidor ha cerrado la conexión
                data += packet

            # Extraer el número entero que nos dice el tamaño en bytes de la imagen
            msg_size = struct.unpack("L", data)[0]

            # 2. Recibir exactamente esa cantidad de bytes (los datos de la imagen)
            frame_data = b""
            while len(frame_data) < msg_size:
                # Recibimos en bloques de hasta 4096 bytes
                packet = self.socket.recv(min(msg_size - len(frame_data), 4096))
                if not packet:
                    return None
                frame_data += packet

            # 3. Decodificar los bytes a una matriz de imagen usando numpy y OpenCV
            nparr = np.frombuffer(frame_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # picamera2 entrega los frames en formato RGB, pero OpenCV trabaja en BGR.
            # Convertimos para que los colores se muestren correctamente.
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            # 4. Aplicar rotación si el usuario lo especifica
            if self._rotation == 90:
                frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            elif self._rotation == 180:
                frame = cv2.rotate(frame, cv2.ROTATE_180)
            elif self._rotation == 270:
                frame = cv2.rotate(frame, cv2.ROTATE_270_COUNTERCLOCKWISE)

            # 5. Escalar si el usuario especificó width y/o height
            if self._width is not None or self._height is not None:
                h, w = frame.shape[:2]
                target_w = self._width if self._width is not None else w
                target_h = self._height if self._height is not None else h
                frame = cv2.resize(frame, (target_w, target_h))

            return frame

        except Exception as e:
            print(f"error al recibir frame: {e}")
            self.disconnect()
            return None
