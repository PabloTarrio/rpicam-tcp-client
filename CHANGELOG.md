# Changelog

Todos los cambios notables de este proyecto se documentan en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/),
y este proyecto sigue [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased]

## [1.0.0] - 2026-03-27

### Added
- Publicación oficial en PyPI como paquete instalable via `pip install rpicam-tcp-client`
- Badge de PyPI en README.md

### Changed
- Metadatos de `pyproject.toml` actualizados: versión, classifiers, URLs del proyecto
- Development Status cambiado a `Production/Stable`

## [0.6.0] - 2026-03-27

### Added
- `examples/config_loader.py`: función helper `load_config()` reutilizable
  por todos los scripts de ejemplo
- `config.example.json`: plantilla de configuración global con todos los
  parámetros comunes (conexion, camara, grabacion, frames, deteccion_movimiento,
  detector_color, calibracion, distancia_visual)
- `config.json` añadido a `.gitignore`

### Changed
- Los 9 scripts de ejemplo adaptados para leer parámetros desde `config.json`
  mediante `load_config()`, manteniendo compatibilidad total con `argparse`

## [0.5.0] - 2026-03-26

### Added
- `examples/03_avanzado/detector_color.py`: detección y rastreo de
  objetos por color en espacio HSV con cálculo de centroide
- `examples/03_avanzado/calibrar_camara.py`: calibración con tablero
  de ajedrez, genera matriz K y coeficientes en archivo `.npz`
- `examples/03_avanzado/medir_distancia_visual.py`: estimación de
  distancia real usando fórmula de triángulos similares D=(W×f)/P
- `examples/README.md`: documentación pedagógica ejemplos 7, 8 y 9
- `README.md`: estructura y ejemplos `03_avanzado` actualizados
- `ROADMAP.md`: Fase 4 completada al 100%

## [0.4.0] - 2026-03-20

### Added
- `examples/02_intermedio/grabar_video.py`: grabación MP4 con
  timestamp y control FPS
- `examples/02_intermedio/detectar_movimiento.py`: detección de
  movimiento con BackgroundSubtractor MOG2 y contornos
- `examples/02_intermedio/guardar_frames.py`: secuencia numerada
  de frames para time-lapse y datasets de IA
- `tqdm` añadida como dependencia en `pyproject.toml`
- `examples/README.md`: documentación completa ejemplos 4, 5 y 6
- `README.md`: estructura y ejemplos 02_intermedio actualizados

## 0.3.0 - 2026-03-16

### Added
- examples/01_basico/guardar_frame.py (captura JPG única)
- examples/README.md pedagógico (tablas, ejercicios)
- README.md principal profesional (badges, instalación 3 comandos)
- **Fase 6 completada**: Documentación final

### Updated
- Estructura ejemplos: mostrar_video.py + mostrar_video_configurado.py + guardar_frame.py

## [0.2.0] - 2026-03-13

### Added
- Tests unitarios completos para `CameraClient` con cobertura del 98%
- Escalado de frames en el cliente (`width`, `height`) mediante `cv2.resize`
- Ejemplo básico de vídeo con parámetros configurables (`mostrar_video_configurado.py`)
- Protocolo de parámetros configurables cliente-servidor (brillo, contraste, saturación, etc.)
- README completo de `examples/` con capturas de pantalla
- Documentación de los ejemplos básicos existentes

### Fixed
- Corrección de colores RGB → BGR en `get_frame`
- Múltiples correcciones de formato con `ruff`

### Docs
- Actualización de `server/README.md`
- Actualización de `ROADMAP.md` con fases completadas

## [0.1.0] - 2026-03-13

### Added
- Estructura inicial del proyecto con `pyproject.toml`
- Cliente TCP `CameraClient` con context manager
- Servidor TCP para Raspberry Pi Camera Module 2 NoIR (`servidor_camara_tcp.py`)
- Ejemplo básico de visualización de vídeo (`mostrar_video.py`)
- Workflow de GitHub Actions con lint (`ruff`) y tests (`pytest`)
- `ROADMAP.md` con fases del proyecto
- Test de humo inicial