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
  * [x] Parámetros: width, height, jpeg_quality, brightness, contrast,
        saturation, sharpness, exposure_time, analogue_gain
  * [x] Valores por defecto en servidor, el cliente solo sobreescribe los que quiera
* [x] Configurar el servidor como servicio `systemd` (arranque automático)

---

## Pendiente

### Fase 3 - 

* [ ] Crear `server/README.md` con instrucciones de instalación en la RPi
* [ ] Documentar el servicio en `server/README.md`

### Fase 4 — Ejemplos de Uso
- [ ] Crear `examples/` con scripts de ejemplo
  - [ ] `examples/01_basico/mostrar_video_configurado.py` — vídeo con parámetros personalizados
  - [ ] `examples/01_basico/guardar_frame.py` — captura y guarda un frame como imagen
  - [ ] `show_video.py` — muestra el vídeo en tiempo real con OpenCV
  - [ ] `save_frame.py` — captura y guarda un frame como imagen
- [ ] Crear `examples/README.md` con descripción de cada ejemplo

### Fase 5 — Tests del Cliente
- [ ] Crear tests unitarios para `CameraClient` en `tests/`
  - [ ] Test de conexión y desconexión
  - [ ] Test del context manager
  - [ ] Test de `get_frame` con un servidor simulado (mock)
- [ ] Cobertura de código con `pytest-cov`
- [ ] CI ejecutando los tests automáticamente en cada PR

### Fase 6 — Documentación Final
- [ ] Escribir `README.md` principal completo
  - [ ] Descripción del proyecto
  - [ ] Requisitos (cliente y servidor)
  - [ ] Instrucciones de instalación
  - [ ] Ejemplo de uso básico
  - [ ] Enlace a `server/README.md` y `examples/README.md`
- [ ] Actualizar `CHANGELOG.md` con versión `0.1.0`

---

## Notas
- Puerto TCP del servidor de cámara: **5001** (el LIDAR usa el 5000)
- Hardware: Raspberry Pi 4 con Camera Module 2 NoIR
- Fecha última actualización: 2026-03-10
- Responsable: Pablo M. Tarrío
- Repositorio: https://github.com/PabloTarrio/rpicam-tcp-client