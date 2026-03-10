# Servidor TCP - Raspberry Pi Camera Module 2 NoIR

Este directorio contiene el script que debe ejecutarse en la **Raspberry PI**.

Se encarga de capturar frames de la cámara y enviarlos por TCP al cliente.

## Requisitos

* Raspberry Pi con cámara Module 2 NoIR conectada
* Ubuntu 24.04 Server instalado en la Raspberry Pi
* Python 3.10 o superior

## Instalación de dependencias

```bash
pip install picamera2 opencv-python
```

## Uso
Ejecute el servidor directamente:

``` bash
python3 servidor_camara_tcp.py
```

## Configuración

Los parámetros se pueden ajustar al inicio del archivo:

| Parámetro    | Valor por defecto | Descripción                |
| ------------ | ----------------- | -------------------------- |
| TCP_PORT     | 5001              | Puerto TCP del servidor    |
| FRAME_WIDTH  | 640               | Ancho del frame en píxeles |
| FRAME_HEIGHT | 480               | Alto del frame en píxeles  |
| JPEG_QUALITY | 80                | Calidad JPEG (0-100)       |

## Protocolo de envío

Cada frame se envía en dos partes:

1. 4 bytes con el tamaño del frame comprimido (entero tipo `Long`)
2. N bytes con los datos del frame en formato JPEG

