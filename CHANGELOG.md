# Changelog

Todos los cambios notables de este proyecto se documentan en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/),
y este proyecto sigue [Semantic Versioning](https://semver.org/lang/es/).

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

## [Unreleased]

- Soporte para más resoluciones
