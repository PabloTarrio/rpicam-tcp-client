""" 
Cliente TCP para conectarse al servidor de la Raspberry Pi Camera y recibir frames.
"""

import socket
import struct
import numpy as np
import cv2

class CameraClient:
    """
    Cliente para recibir frames de video desde la Raspberry Pi a través de TCP.
    """
    def __init__(self, host: str, port: int = 5001):
        """
        Inicializa el cliente.
        
        Args:
            host (str): Dirección IP de la Raspberry Pi.
            port (int): Puerto del servidor (por defecto 5001).
        """
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False

    def connect (self):
        """
        Conecta al servidor TCP de la cámara
        """
        if self.connected:
            raise Exception ("Ya estás conectado al servidor")
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.connected = True
        print (f"Conectado a la cámara en {self.host}:{self.port}")

    def disconnect(self):
        """
        Cierra la conexión con el servidor
        """
        if self.connected and self.socket:
            self.socket.close()
            self.connected = False
            print ("Desconectado del servidor de la cámara")

    def __enter__(self):
        """
        Soporte para context manager 'with'.
        """
        self.connect()
        return self

    def __exit__ (self, exc_type, exc_val, exc_tb):
        """
        Cierra  automáticamente al salir del 'with'
        """
        self.disconnect()

    def get_frame (self):
        """
        Recibir un frame de video del servidor y lo decodifica.

        Returns:
            np.ndarray: La imagen decodificada lista para mostrar con OpenCV,
                        o None si hubo un error de conexión
        """
        if not self.connected or not self.socket:
            raise Exception ("No hay conexión con el servidor")
        
        try:
            #1. Recibir los 4 bytes que indican el tamaño del frame (empaquetado como 'Long')
            payload_size = struct.calcsize("L")
            data = b""

            # Asegurarnos de recibir esos 4 bytes completos
            while len(data) < payload_size:
                packet = self.socket.recv(payload_size - len(data))
                if not packet:
                    return None # El servidor ha cerrado la conexión
                data += packet

            # Extraer el número entero que nos dice el tamaño en bytes de la imagen
            msg_size = struct.unpack("L", data)[0]

            #2. Recibir exactamente esa cantidad de bytes (los datos de la imagen)
            frame_data = b""
            while len(frame_data) < msg_size:
                # Recibimos en bloques de hasta 4096 bytes
                packet = self.socket.recv(min(msg_size - len(frame_data), 4096))
                if not packet:
                    return None
                frame_data += packet
            
            #3. Decodificar los bytes recibidos a una matriz (array) de imagen usando numpy y OpenCV
            nparr = np.frombuffer(frame_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            return frame
        
        except Exception as e:
            print(f"error al recibir frame: {e}")
            self.disconnect()
            return None