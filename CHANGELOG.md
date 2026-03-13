# Changelog

Todos los cambios notables de este proyecto se documentan en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/),
y este proyecto sigue [Semantic Versioning](https://semver.org/lang/es/).

---

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

---

## [0.1.0] - 2026-03-13

### Added
- Estructura inicial del proyecto con `pyproject.toml`
- Cliente TCP `CameraClient` con context manager
- Servidor TCP para Raspberry Pi Camera Module 2 NoIR (`servidor_camara_tcp.py`)
- Ejemplo básico de visualización de vídeo (`mostrar_video.py`)
- Workflow de GitHub Actions con lint (`ruff`) y tests (`pytest`)
- `ROADMAP.md` con fases del proyecto
- Test de humo inicial

---

## [Unreleased]

- Rotación de frames en el cliente (`rotation`)
- Soporte para más resoluciones
