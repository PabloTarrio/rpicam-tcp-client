"""
Tests unitarios para CameraClient.

Usamos unittest.mock para simular el servidor TCP, de forma que
los tests se ejecuten sin necesidad de una Raspberry Pi real.
"""

import struct
import json
import numpy as np
import cv2
import pytest
from unittest.mock import MagicMock, patch

from rpicam_tcp_client import CameraClient


# =============================================================================
# FIXTURES
# =============================================================================

def make_fake_frame(width= 640,height= 480):
    """
    Crea un frame JPEG falso como lo enviaría el servidor:
    - Array BGR de numpy
    - Comprimido en JPEG
    - Empaquetado con cabecera de 4 bytes
    """

    # Frame de color sólido azul (BGR)
    frame_bgr= np.zeros((height, width, 3),dtype=np.uint8)
    frame_bgr[:,:]=(255,0,0)

    # El servidor envía RGB, no BGR
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

    # Comprimir a JPEG como haría el servidor
    _, buffer= cv2.imencode(".jpg", frame_rgb, [cv2.IMWRITE_JPEG_QUALITY, 80])
    jpeg_bytes= buffer.tobytes()

    # Empaquetar con cabecera de 4 bytes (protocolo TCP)
    header= struct.pack("L", len(jpeg_bytes))
    return header+jpeg_bytes

def make_fake_socket(frame_data: bytes):
    """
    Crea un socket simulado que devuelve frame_data byte a byte
    cuando se le llama a recv().
    """
    mock_socket = MagicMock()
    # Simula recv() devolviendo los bytes del frame en trozos
    mock_socket.recv.side_effect = [
        bytes([b]) for b in frame_data
    ] + [b""] #b"" simula cierre de conexion

    return mock_socket

# =============================================================================
# TESTS: __init__ y validación de parámetros
# =============================================================================

class TestInit:
    def test_host_y_port_por_defecto(self):
        cam = CameraClient(host="192.168.1.1")
        assert cam.host =="192.168.1.1"
        assert cam.port == 5001

    def test_port_personalizado(self):
        cam = CameraClient(host="192.168.1.1", port=9000)
        assert cam.port == 9000
    
    def test_estado_inicial_desconectado(self):
        cam = CameraClient(host="192.168.1.1")
        assert cam.connected is False
        assert cam.socket is None

    def test_rotation_valido(self):
        for rot in (0, 90, 180, 270):
            cam = CameraClient(host="192.168.1.1", rotation=rot)
            assert cam._rotation == rot
    
    def test_width_y_height_no_van_al_json(self):
        cam = CameraClient(host="192.168.1.1", width=640, height=480)
        assert "width" not in cam._params
        assert "height" not in cam._params
        assert cam._width == 640
        assert cam._height == 480
    
    def test_parametros_servidor_van_al_json(self):
        cam = CameraClient (
            host="192.168.1.1",
            jpeg_quality=60,
            brightness=0.1,
            contrast=1.2,
            saturation=0.8,
            sharpness=2.0,
        )
        assert cam._params["jpeg_quality"] == 60
        assert cam._params["brightness"] == 0.1
        assert cam._params["contrast"] == 1.2
        assert cam._params["saturation"] == 0.8
        assert cam._params["sharpness"] == 2.0

    def test_parametros_none_no_val_al_json(self):
        cam = CameraClient(host="192.168.1.1")
        assert cam._params == {}

# =============================================================================
# TESTS: connect / disconnect
# =============================================================================

class TestConectarDesconectar:
    def test_connect_cambia_estado(self):
        cam = CameraClient(host="192.168.1.1")
        with patch ("socket.socket") as mock_sock_class:
            mock_sock = MagicMock()
            mock_sock_class.return_value = mock_sock

            # Simular recv del JSON de parámetros
            params_json = json.dumps({}).encode("utf-8")
            mock_sock.recv.return_value = b""

            cam.connect()
            assert cam.connected is True

    def test_disconnect_cambia_estado(self):
        cam = CameraClient(host="192.168.1.1")
        cam.connected = True
        cam.socket = MagicMock()
        cam.disconnect()
        assert cam.connected is False

    def test_connect_doble_lanza_error(self):
        cam = CameraClient(host= "192.168.1.1")
        cam.connected = True
        with pytest.raises(Exception, match="Ya estás conectado"):
            cam.connect()
    
    def test_context_manager_conecta_y_desconecta(self):
        cam = CameraClient(host="192.168.1.1")
        with patch ("socket.socket") as mock_sock_class:
            mock_sock = MagicMock()
            mock_sock_class.return_value = mock_sock
            with cam:
                assert cam.connected is True
            assert cam.connected is False

# =============================================================================
# TESTS: get_frame — rotación y escalado
# =============================================================================

class TestGetFrame:

    def _get_frame_con_socket (self, cam, frame_data):
        """Helper: inyecta socket simulado y llama get_frame()"""
        cam.connected = True
        cam.socket = make_fake_socket(frame_data)
        return cam.get_frame()
    
    def test_frame_tiene_dimensiones_correctas(self):
        cam = CameraClient (host="192.168.1.1")
        frame = self._get_frame_con_socket(cam, make_fake_frame(640,480))
        assert frame is not None
        assert frame.shape == (480, 640, 3)

    def test_escalado_width_y_height(self):
        cam = CameraClient(host="192.168.1.1", width=320, height=240)
        frame = self._get_frame_con_socket(cam, make_fake_frame(640, 480))
        assert frame is not None
        assert frame.shape == (240, 320, 3)

    def test_escalado_solo_width(self):
        cam = CameraClient(host="192.168.1.1", width=320)
        frame = self._get_frame_con_socket(cam, make_fake_frame(640, 480))
        assert frame is not None
        assert frame.shape[1] == 320

    def test_escalado_solo_height(self):
        cam = CameraClient(host="192.168.1.1", height=240)
        frame = self._get_frame_con_socket(cam, make_fake_frame(640, 480))
        assert frame is not None
        assert frame.shape[0] == 240

    def test_rotacion_180(self):
        cam = CameraClient(host="192.168.1.1", rotation=180)
        frame_orig = self._get_frame_con_socket(
            CameraClient(host="192.168.1.1"), make_fake_frame(640, 480)
        )
        cam.connected = True
        cam.socket = make_fake_socket(make_fake_frame(640, 480))
        frame_rot = cam.get_frame()
        expected = cv2.rotate(frame_orig, cv2.ROTATE_180)
        assert np.array_equal(frame_rot, expected)

    def test_rotacion_90(self):
        cam = CameraClient(host="192.168.1.1", rotation=90)
        frame = self._get_frame_con_socket(cam, make_fake_frame(640, 480))
        # 90° → ancho y alto se intercambian
        assert frame.shape == (640, 480, 3)

    def test_rotacion_270(self):
        cam = CameraClient(host="192.168.1.1", rotation=270)
        frame = self._get_frame_con_socket(cam, make_fake_frame(640, 480))
        # 270° → ancho y alto se intercambian
        assert frame.shape == (640, 480, 3)

    def test_sin_rotacion_dimensiones_intactas(self):
        cam = CameraClient(host="192.168.1.1", rotation=0)
        frame = self._get_frame_con_socket(cam, make_fake_frame(640, 480))
        assert frame.shape == (480, 640, 3)

    def test_conexion_perdida_devuelve_none(self):
        cam = CameraClient(host="192.168.1.1")
        cam.connected = True
        cam.socket = MagicMock()
        cam.socket.recv.return_value = b""  # simula cierre
        frame = cam.get_frame()
        assert frame is None

# =============================================================================
# TEST ADICIONALES - Subir cobertura al 95%+
# =============================================================================
class TestParametrosExtendidos:
    def text_exposure_time_va_al_json(self):
        cam = CameraClient(host="192.168.1.1", exposure_time=10000)
        assert cam._params["exposure_time"] == 10000

    def test_analogue_gain_va_al_json(self):
        cam = CameraClient(host="192.168.1.10", analogue_gain=2.5)
        assert cam._params["analogue_gain"] == 2.5
    
    def test_rotation_invalido_mensaje_correcto(self):
        with pytest.raises (ValueError, match="Rotación debe ser"):
            CameraClient(host="192.168.1.1", rotation=45)

class TestDisconnect:
    def test_disconnect_sin_conexion_no_falla(self):
        """disconnect() cuando no hay conexión no debe lanzar excepción."""
        cam = CameraClient(host="192.168.1.1")
        cam.disconnect()  # No debe lanzar nada
        assert cam.connected is False

    def test_disconnect_cierra_socket(self):
        cam = CameraClient(host="192.168.1.1")
        mock_sock = MagicMock()
        cam.socket = mock_sock
        cam.connected = True
        cam.disconnect()
        mock_sock.close.assert_called_once()
        assert cam.connected is False


class TestGetFrameErrores:
    def test_get_frame_sin_conexion_lanza_error(self):
        cam = CameraClient(host="192.168.1.1")
        cam.connected = False
        with pytest.raises(Exception, match="No hay conexión"):
            cam.get_frame()

    def test_get_frame_excepcion_devuelve_none(self):
        """Si el socket lanza una excepción inesperada, get_frame devuelve None."""
        cam = CameraClient(host="192.168.1.1")
        cam.connected = True
        cam.socket = MagicMock()
        cam.socket.recv.side_effect = OSError("fallo de red")
        result = cam.get_frame()
        assert result is None
