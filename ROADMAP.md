# ROADMAP DEL PROYECTO - rpicam-tcp-client

## COMPLETADO

### Fase 1 - Estructura del proyecto y CI

* [x] Crear repositorio GitHub `rpicam-tcp-client`
* [x] Estructura de carpetas (`src/`, `server/`, `tests/`, `.github/`)
* [x] `.gitignore` configurado
* [x] `pyproject.toml` con dependecias (`numpy`, `opencv-python`) y metadatos
* [x] Configuración de `ruff` en `pyproyect.toml`
* [x] Entorno virtual `.venv` creado e instalado en modo editable
* [x] Workflow de CI en `./github/workflows/ci.yml` (lint + tests)
* [x] Protección de rama `main` (PR obligatorio, Squash and Merge)

### Fase 2 - Librería Cliente Python

* [x] `src/rpicam_tcp_client/client.py` — Clase `CameraClient`

    * [x] `__init__.py` con host y puerto 5001
    * [x] `connect` / `disconnect`
    * [x] Context manager (`__enter__` / `__exit__`)
    * [x] `get_frame` - Recibe y decodifica frames por TCP

* [x] `src/rpicam_tcp_client/__init__.py` - expone `CameraClient`
* [x] Test de humo - la librería se importa correctamente
* [x] CI pasando en verde

### Fase 3 — Servidor TCP en Raspberry Pi

* [x] Crear `server/servidor_camara_tcp.py`
  * [x] Conectar a la cámara con `picamera2`
  * [x] Capturar frames y comprimirlos en JPEG
  * [x] Enviar encabezado de 4 bytes con el tamaño del frame
  * [x] Enviar el frame por TCP al cliente conectado
  * [x] Manejo de desconexión del cliente
  * [x] Manejo de cierre limpio (Ctrl+C)
  * [x] Protocolo de parámetros configurables vía JSON
  * [x] Captura resolución fija (1920*1080), los escalados se aplican en el cliente.
  * [x] Parámetros: width, height, jpeg_quality, brightness, contrast,
        saturation, sharpness, exposure_time, analogue_gain
  * [x] Valores por defecto en servidor, el cliente solo sobreescribe los que quiera
* [x] Configurar el servidor como servicio `systemd` (arranque automático)
* [x] Crear `server/README.md` con instrucciones de instalación en la RPi
* [x] Documentar el servicio en `server/README.md`

### Fase 4 — Ejemplos de Uso
- [x] Crear `examples/` con scripts de ejemplo
  - [x] `examples/01_basico/guardar_frame.py` — captura y guarda un frame como imagen
  - [x] `examples/01_basico/mostrar_video.py` — vídeo con parámetros personalizados
  - [x] `examples/01_basico/mostrar_video_configurado.py` — vídeo con parámetros personalizados
  - [x] `examples/02_intermedio/grabar_video.py` - grabar video con timestamp integrado
  - [x] `examples/02_intermedio/detectar_movimiento.py` - detección de movimiento con BackgroundSubtractor MOG2
  - [x] `examples/o2_intermedio/guardar_frames.py` - Guardar multiples frames para generar time-lapse o datasets
  - [x] `examples/03_avanzado/detector_color.py`
  - [x] `examples/03_avanzado/calibrar_camara.py`
  - [x] `examples/03_avanzado/medir_distancia_visual.py`
- [x] `examples/README.md` — documentación pedagógica de los ejemplos
- [x] `examples/images/` — capturas representativas de los ejemplos
- [x] Crear `examples/README.md` con descripción de cada ejemplo
- [x] Publicacion badges en README
- [x] Creacion de archivos CHANGELOG, CONTRIBUTING, LICENSE

> NOTA de DISEÑO:
>  * `width` y `height` se aplican localmente en el cliente mediante `cv2.resize`; ya no se envían
>     al servidor para evitar recortes parciales del sensor
> * `rotation` se aplica localmente en el cliente con `cv2.rotate`; no se envía al servidor

### Fase 5 - Tests del cliente

* [x] `tests/test_camera_client.py` — 27 tests unitarios para `CameraClient`
  * [x] Tests de `__init__`: parámetros JSON, parámetros locales, validación `rotation`
  * [x] Tests de `connect` / `disconnect` con socket simulado (mock)
  * [x] Tests de context manager (`with`)
  * [x] Tests de `get_frame`: escalado, rotación 0/90/180/270, pérdida de conexión
* [x] Cobertura del 98% con `pytest-cov`
* [x] `pyproject.toml` actualizado: `pytest-cov` en `dev`, `[tool.pytest.ini_options]`,
      `[tool.coverage.report]` con `fail_under = 95`
* [x] CI ejecutando los tests automáticamente en cada PR

### Fase 6 — Documentación Final
- [x] Escribir `README.md` principal completo
  - [x] Descripción del proyecto
  - [x] Requisitos (cliente y servidor)
  - [x] Instrucciones de instalación
  - [x] Ejemplo de uso básico
  - [x] Enlace a `server/README.md` y `examples/README.md`
- [x] Actualizar `CHANGELOG.md` con versión `0.1.0`

### Fase 7 - Archivo de configuración global (v0.6.0)
- [x] Diseñar `config.example.json` con todos los parámetros comunes
- [x] Añadir `config.json` al `.gitignore`
- [x] Crear función helper `load_config()` reutilizable por todos los scripts
- [x] Adaptar 9 scripts de ejemplo para usar load_config()
- [x] Actualizar `examples\README.md` con instrucciones de configuración
- [x] Actualizar `README.md` principal con sección de primeros pasos
- [x] Documentar en `README.md` problema conocido de fuente Qt con opencv-python
      y su solución (`cp dejavi fonts -> .venv/cv2/qt/fonts/`)

## Pendiente

### Fase 8 - Publicacion en PyPI (v1.0.0)
- [ ] Revisar y completar metadatos en `pyproject.toml`
- [ ] Generar el paquete con `build`
- [ ] Publicar en TestPyPI y verificar instalación
- [ ] Publicar en PyPI oficial
- [ ] Actualizar `README.md` con badge e instrucciones `pip install`


### IDEAS FUTURAS
- [ ] Grabación activada por detección de movimiento (tipo cámara de seguridad)
- [ ] Detección de objetos con IA (YOLOv8-nano o MobileNet SSD)
- [ ] Soporte multicliente en el servidor (threading/asyncio)
---

## Notas
- Puerto TCP del servidor de cámara: **5001** (el LIDAR usa el 5000)
- Hardware: Raspberry Pi 4 con Camera Module 2 NoIR
- Fecha última actualización: 2026-03-27
- Responsable: Pablo M. Tarrío
- Repositorio: https://github.com/PabloTarrio/rpicam-tcp-client