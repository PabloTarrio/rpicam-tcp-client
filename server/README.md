# Servidor TCP - Raspberry Pi Camera Module 2 NoIR

Este directorio contiene el script que debe ejecutarse en la **Raspberry PI**.

Se encarga de capturar frames de la cámara, aplicar la configuración solicitada por el cliente y enviarlos por TCP al cliente.

## Requisitos

* Raspberry Pi con cámara Module 2 NoIR conectada
* Ubuntu 24.04 Server instalado en la Raspberry Pi
* Python 3.10 o superior

## Instalación de dependencias

```bash
sudo apt install -y libcap-dev libcamera-ipa
sudo pip3 install picamera2 opencv-python --break-system-packages
```

## Uso
Ejecute el servidor directamente:

``` bash
python3 servidor_camara_tcp.py
```

El servidor quedará escuchando en el puerto 5001 hasta que un cliente se conecte. Cuando el cliente se desconecte, volverá a esperar al siguiente. Para detenerlo pulse `Ctrl+C`

## Configuración

El servidor arranca con estos valores. El cliente puede sobreescribir cualquiera de ellos al conectarse (ver sección **Protocolo**)

| Parámetro    | Valor por defecto | Descripción                      |
| ------------ | ----------------- | ------------------------------   |
| TCP_HOST     | 0.0.0.0           | Escucha en todas las interfaces  |
| TCP_PORT     | 5001              | Puerto TCP del servidor          |
| FRAME_WIDTH  | 640               | Ancho del frame en píxeles       |
| FRAME_HEIGHT | 480               | Alto del frame en píxeles        |
| JPEG_QUALITY | 80                | Calidad JPEG (0-100)             |

## Protocolo

La comunicación cliente-servidor tiene dos fases:

#### Fase 1 - Negociación de parámetros (al conectarse):

Nada más conectarse, el cliente envía un archivo JSON con los parámetros que desea. El servidor los aplica sobre sus valores
por defecto: solo se sobreescriben los parámetros que el cliente especifica explícitamente.

El JSON envía con el mismo protocolo que los frames:

1. 4 bytes con el tamaño del frame comprimido (entero tipo `Long`)
2. N bytes con los datos del frame en formato JPEG

Parametros configurables por el cliente:

| Parámetro     | Tipo  | Descripción                           |
| ------------- | ----- | ------------------------------------- |
| width         | int   | Ancho del frame en píxeles            |
| height        | int   | Alto del frame en píxeles             |
| jpeg_quality  | int   | Calidad JPEG (0-100)                  |
| brightness    | float | Brillo de la imagen                   |
| contrast      | float | Contraste de la imagen                |
| saturation    | float | Saturación de la imagen               |
| sharpness     | float | Nitidez de la imagen                  |
| exposure_time | int   | Tiempo de exposición en microsegundos |
| analogue_gain | float | Ganancia analógica del sensor         |

Ejemplo de JSON enviado por el cliente:

``` json
{
    "width": 640,
    "height": 480,
    "jpeg_quality": 60
 }
```

Si el cliente no especifica ningún parámetro, envía `{}` y el servidor usas sus valores por defecto para todo.

#### Fase 2 - Streaming de frames:

Una vez configurada la cámara, el servidor envía frames continuamente. Cada frame se envía en dos partes:

1. 4 bytes con el tamaño del frame comprimido (entero tipo `Long`)
2. N bytes con los datos del frame en formato JPEG

## Servicio `systemd`

El servidor está configurado para arrancar automáticament con el sistema como servicio `camara-tcp.service`.

### Comandos útiles:

``` bash
# Ver el estado del servicio
sudo systemctl status camara-tcp.service

# Reiniciar el servicio (tras actualizar el script)
sudo systemctl restart camara-tcp.service

# Ver los logs en tiempo real
sudo journalctl -u camara-tcp.service -f
```
