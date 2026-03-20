# Ejemplos de `rpicam-tcpclient` - Aprendizaje progresivo

Los ejemplos están organizados por "niveles de dificultad" para facilitar un aprendizaje estructurado:

* 01_básico/        # Primeros pasos
* 02_intermedio/    # Análisis y exportación
* 03_avanzado/      # Procesamiento avanzado

**Antes de empezar**

1. Servidor corriendo: `sudo systemctl status camara-tcp.service`
2. Instalación: `pip install -e .`
3. Probar conexión básica: `python examples/01_basico/mostrar_video.py --host <Raspberry_Pi_IP>`

---

## `01_basico/` - Primeros pasos

### 1. `mostrar_video.py` - Tu primera imagen

**Objetivo:** Ver video en tiempo real desde la Raspberry Pi usando valores por defecto

**¿Qué aprenderás?**

- Conectar con 'CameraClient'
- Bucle de recepción de frames
- Mostrar con OpenCV

**Uso:**

```bash
python mostrar_video.py --host <Raspberry_Pi_IP>
```

**Salida esperada**

```text
Conectado a la cámara en 172.16.127.78:5001
    Parámetros enviados: ninguno (valores por defecto)
Recibiendo video. Pulsa q para salir.
```

![Ejemplo básico 01](images/01_basico_mostrar_video.png)

**Controles**

`q` para cerrar la ventana y finalizar la ejecución del script.


### 2. `mostrar_video_configurado.py` - Configuración desde el cliente

**Objetivo:** Personalizar la cámara (resolución, brillo, rotación, etc.)

**¿Qué aprenderás?**

- Todos los parámetro de 'CameraClient'
- Escalado y rotación local
- Uso de `--help` completo con `argparse`

**Uso:**

```bash
# Resolución reducida + saturación baja
python mostrar_video_configurado.py --host <Raspberry_Pi_IP> --width 640 --height 480 --saturation 0.6

# Rotación + contraste alto
python mostrar_video_configurado.py --host <Raspberry_Pi_IP> --rotation 180 --contrast 1.2

# Ejemplo de uso completo de los parámetros
python mostrar_video_configurado.py --host <Raspberry_Pi_IP> --width 640 --height 480 --saturation 0.6 --brightness 0.1 --rotation 180
```

**Parámetros disponibles:**

| Arg | Tipo | Rango | Dónde se aplica | Descripción |
|-----|------|-------|-----------------|-------------|
| `--width` | `int` | 64-1920 | **Cliente** | Ancho destino (`cv2.resize`) |
| `--height` | `int` | 64-1080 | **Cliente** | Alto destino (`cv2.resize`) |
| `--jpeg_quality` | `int` | 0-100 | **Servidor** | Calidad JPEG |
| `--brightness` | `float` | -1.0 a 1.0 | **Servidor** | Brillo (picamera2) |
| `--contrast` | `float` | 0.0-32.0 | **Servidor** | Contraste (picamera2) |
| `--saturation` | `float` | 0.0-32.0 | **Servidor** | Saturación (0.0=gris) |
| `--sharpness` | `float` | 0.0-16.0 | **Servidor** | Nitidez (picamera2) |
| `--exposure_time` | `int` | 114-694267 µs | **Servidor** | Exposición manual |
| `--analogue_gain` | `float` | 1.0-16.0 | **Servidor** | Ganancia analógica |
| `--rotation` | `int` | 0,90,180,270 | **Cliente** | Rotación (`cv2.rotate`) |

**Salida esperada:**

```text
Conectado a la cámara en 172.16.127.78:5001
  Parámetros enviados: {'saturation': 0.6}
```

![Ejemplo básico 02](images/01_basico_mostrar_video_configurado.png)

**Controles:**

`q` para cerrar la ventana y finalizar la ejecución del script.

### 3. `guardar_frame.py` - Capturar y guardar una fotografía

**Objetivo:** Capturar UN SOLO frame desde la Rapsberry Pi y guardarlo como imagen JPG en el ordenador remoto. Perfecto para capturas puntuales

**¿Qué aprenderás?**

* Uso mínimo de `CameraClient`: un solo get_frame() sin bucle

* Context manager `with`: connect/disconnect automático.

* Guardar imágenes con OpenCV (`cv2.imwrite`).

* Diferencia entre parámetros servidor (`jpeg_quality`, `brightness`) y parámetros cliente (`width`, `height`, `rotation`)

**Uso:**

```bash
# Ejemplo básico: usar valores por defecto
python guardar_frame.py --host <Raspberry_Pi_IP>

# Guardar con nombre personalizado
python guardar_frame.py --host <Raspberry_Pi_IP> --output foto.jpg

# Escalado local a 640x480
python guardar_frame.py --host <Raspberry_Pi_IP> --width 640 --height 480 --output captura_640x480.jpg

# Rotación 90° + brillo configurado en el servidor
python guardar_frame.py --host <Raspberry_Pi_IP> --rotation 90 --brightness 0.4 --output foto_rotada.jpg
```

**Parámetros disponibles:**

| Arg           | Tipo  | Rango        | Dónde se aplica | Descripción                                   |
| ------------- | ----- | ------------ | --------------- | --------------------------------------------- |
| --host        | str   | -            | -               | IP Raspberry Pi (obligatorio)                 |
| --output      | str   | -            | -               | Archivo JPG destino (default captura_cam.jpg) |
| --width       | int   | 64-1920      | Cliente         | Ancho destino (cv2.resize)                    |
| --height      | int   | 64-1080      | Cliente         | Alto destino (cv2.resize)                     |
| --rotation    | int   | 0,90,180,270 | Cliente         | Rotación (cv2.rotate)                         |
| --jpegquality | int   | 0-100        | Servidor        | Calidad JPEG                                  |
| --brightness  | float | -1.0 a 1.0   | Servidor        | Brillo (picamera2)                            |

**Salida esperada (ejemplo):**

```text
Conectando a cámara en 172.16.127.78:5001...
Conectado a la cámara en 172.16.127.78:5001
    Parámetros enviados: ninguno (valores por defecto)
Conectado. Capturando frame...
Frame capturado: 1920x1080 píxeles (rotation=0°, width=None, height=None)
Frame guardado: /ruta/completa/frame.jpg
Desconectado del servidor de la cámara
```
> NOTA: El script se cierra automáticamente tras guardar. No hay ventana ni bucle.

## `02_intermedio` - Análisis y exportación

### 4. `grabar_video.py` - Grabar video MP4 con timestamps

**Objetivo:** Grabar vídeo contínuo desde la cámara en formato MP4 con timestamp superpuesto.

**¿Qué aprenderás?**

- Uso de `cv2.VideoWriter` para crear archivos MP4
- Superponer texto en frames con `cv2.putText`
- Control de duración con `frames_total = duration * fps`
- Limitación real de FPS por red TCP (reto en ejercicios)

**Uso:**

```bash
# Grabación básica 30 segundos
python grabar_video.py --host <Raspberry_Pi_IP>

# Grabación con duración personalizada
python grabar_video.py --host <Raspberry_Pi_IP> --duration 60 --output experimento.mp4

# Grabación con rotación
python grabar_video.py --host <Raspberry_Pi_IP> --duration 10 --rotation 180
```

**Parámetros Disponibles:**

| Arg        | Tipo | Descripción                             |
| ---------- | ---- | --------------------------------------- |
| --host     | str  | IP Raspberry Pi (obligatorio)           |
| --duration | int  | Duración en segundos (default 30)       |
| --fps      | int  | FPS configurado (default 15)            |
| --output   | str  | Archivo MP4 destino (default video.mp4) |
| --width    | int  | Ancho frame (default 640)               |
| --height   | int  | Alto frame (default 480)                |
| --rotation | int  | Rotación 0,90,180,270 (default 0)       |

**Salida esperada:**

```text
Grabando 30s a 15FPS = 450 frames
Output: video.mp4 (640x480)
Conectado a la cámara en 172.16.127.78:5001
Grabación iniciada. Pulsa 'q' en ventana para parar.
Progreso: 100.0% (450/450)
Grabación finalizada.
Video guardado: video.mp4
```

**Controles:** `q` en ventana para parar antes del límite

### 5. `detectar_movimiento.py` - Grabar video MP4 con timestamps

**Objetivo:** Detectar movimiento en tiempo real usando Background Subtraction

**¿Qué aprenderás?**

- Background Subtraction con `cv2.BackgorundSubtractionMOG2()`
- Encontrar regiones con cambios con `cv2.findContours()`
- Dibujar cajas sobre objetos con `cv2.boundingRect()`
- Filtrar ruido con umbral de área mínima

**Uso:**

```bash
# Detección básica
python detectar_movimiento.py --host <Raspberry_Pi_IP>

# Más sensible
python detectar_movimiento.py --host <Raspberry_Pi_IP> --umbral 10 --area_minima 200

# Con rotación
python detectar_movimiento.py --host <Raspberry_Pi_IP> --rotation 180
```

**Parámetros Disponibles:**

| Arg           | Tipo | Descripción                                         |
| ------------- | ---- | --------------------------------------------------- |
| --host        | str  | IP Raspberry Pi (obligatorio)                       |
| --umbral      | int  | Sensibilidad 1-100, menor=más sensible (default 25) |
| --area_minima | int  | Área mínima px² para detectar (default 500)         |
| --width       | int  | Ancho frame (default 640)                           |
| --height      | int  | Alto frame (default 480)                            |
| --rotation    | int  | Rotación 0,90,180,270 (default 0)                   |


**Salida esperada:**

```text
Conectado a la cámara en 172.16.127.78:5001
    Parámetros enviados: ninguno (valores por defecto)
Detectando movimiento. Pulsa 'q' para salir.
Área mínima: 500px2 | Umbral: 25
```

**Controles:** `q` en ventana para parar antes del límite