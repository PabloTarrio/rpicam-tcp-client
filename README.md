# rpicam-tcp-client

[![CI](https://github.com/PabloTarrio/rpicam-tcp-client/actions/workflows/ci.yml/badge.svg)](https://github.com/PabloTarrio/rpicam-tcp-client/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Coverage](https://img.shields.io/badge/coverage-98%25-brightgreen)](https://github.com/PabloTarrio/rpicam-tcp-client/actions)

Librería Python para acceder remotamente a la **Raspberry Pi Camera Module 2 NoIR**
mediante TCP.

---

## Características

- **Acceso remoto** — conecta desde cualquier PC en la misma red
- **Parámetros configurables** — brillo, contraste, saturación, exposición, etc.
- **Escalado y rotación locales** — `cv2.resize` y `cv2.rotate` en el cliente
- **Reconexión automática** — reintentos configurables si falla la conexión
- **Plug & play** — API simple con context managers

---

## Requisitos

**En la Raspberry Pi (servidor):**
- Raspberry Pi 4 con Ubuntu 24.04 Server
- Camera Module 2 NoIR conectada
- Python 3.10+
- `picamera2`, `opencv-python`

**En tu PC (cliente):**
- Python 3.10+
- Conexión de red a la Raspberry Pi

---

## Instalación

**Cliente (PC)**
```bash
git clone https://github.com/PabloTarrio/rpicam-tcp-client.git
cd rpicam-tcp-client
pip install -e .
```

**Servidor (RPi)**
```bash
cd server && pip install -r requirements.txt
sudo cp camara-tcp.service /etc/systemd/system/
sudo systemctl enable --now camara-tcp.service
```
**Características:**

* Acceso remoto: conecta desde cualquier PC de la red.

* Parámetros configurables: brillo, contraste, saturación, etc.

* Escalado/rotación locales: `cv2.resize()`, `cv2.rotate()` en cliente

* Tests 98%: pytest con mocks (sin RPi real)

## Uso Básico

```python
from rpicam_tcp_client import CameraClient
import cv2

with CameraClient (
    host= TU_RASPBERRI_PI_IP,
    jpeg_quality= 60,
    saturation= 0.8,
    rotation= 180,
    width= 640,
    height= 480,
) as cam:
    while True:
        frame = cam.get_frame()
        cv2.imshow("Cámara", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
```

## Parámetros disponibles

| Parámetro     | Tipo  | Rango         | Dónde se aplica | Descripción           |
| ------------- | ----- | ------------- | --------------- | --------------------- |
| jpeg_quality  | int   | 0-100         | Servidor        | Calidad JPEG          |
| brightness    | float | -1.0 a 1.0    | Servidor        | Brillo                |
| contrast      | float | 0.0-32.0      | Servidor        | Contraste             |
| saturation    | float | 0.0-32.0      | Servidor        | Saturación            |
| sharpness     | float | 0.0-16.0      | Servidor        | Nitidez               |
| exposure_time | int   | 114-694267 µs | Servidor        | Exposición manual     |
| analogue_gain | float | 1.0-16.0      | Servidor        | Ganancia analógica    |
| width         | int   | 64-1920       | Cliente         | Escalado (cv2.resize) |
| height        | int   | 64-1080       | Cliente         | Escalado (cv2.resize) |
| rotation      | int   | 0,90,180,270  | Cliente         | Rotación (cv2.rotate) |

## Ejemplos

Consulta [README.md](/examples/README.md) para la documentación completa.

```bash
# Ejemplo 1: vídeo en tiempo real (valores por defecto)
python examples/01_basico/mostrar_video.py --host <RASPBERRY_PI_IP>

# Ejemplo 2: vídeo con parámetros personalizados
python examples/01_basico/mostrar_video_configurado.py --host <RASPBERRY_PI_IP> --width 640 --height 480 --saturation 0.8 --rotation 180

# Ejemplo 3: guardar un frame
python examples/01_basico/guardar_frame.py --host <RASPBERRY_PI_IP>

# Ejemplo 4: grabar video MP4 con timestamp
python examples/02_intermedio/grabar_video.py --host <RASPBERRY_PI_IP> --duration 10 --fps 15 --output video.mp4

# Ejemplo 5: detección de movimiento en tiempo real
python examples/02_intermedio/detectar_movimiento.py --host <RASPBERRY_PI_IP> --umbral 10 --area_minima 200

```

## Estructura del proyecto

```text
rpicam-tcp-client/
|___ src/rpicam_tcp_client/
|    |___ __init__.py
|    |___ client.py
|___ server/
|    |___ servidor_camara_tcp.py
|    |___ README.md
|___ examples/
|    |___01_basico/
|    |    |___ guardar_frame.py
|    |    |___ mostrar_video.py
|    |    |___ mostrar_video_configurado.py
|    |___02_intermedio/
|    |    |___ grabar_video.py
|    |    |___ detectar_movimiento.py
|    |___ images/
|    |___ README.md
|___ tests/
|    |___test_smoke.py
|    |___test_camera_client.py
|___pyproyect.toml
```

## Desarollo

```bash
# Instalar dependecias de desarollo
pip install -e "[.dev]"

# Ejecutar tests con cobertura
pytest

# Ejecutar linting
ruff check .
ruff format .
```

## Documentación adicional

* [server/README.md](server/README.md) - Instalación del servidor en la Raspberry Pi
* [examples/README.md](examples/README.md) - Guía de ejemplos
* [CHANGELOG.md](changelog.md) - Historial de cambios

## Licencia

Este proyecto esta bajo licencia MIT. Ver [LICENSE](LICENSE.md) para más detalles.

