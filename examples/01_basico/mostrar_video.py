"""
=============================================================================
EJEMPLO 1: Tu primera imagen de la cámara — Tutorial paso a paso
=============================================================================

OBJETIVO:
    Mostrar video en tiempo real desde la Raspberry Pi usando valores por
    defecto del servidor.

REQUISITOS PREVIOS:
    - Servidor corriendo: `sudo systemctl status camara-tcp.service`
    - Conocer IP de la Raspberry Pi: `ping 172.16.127.78`
    - (Opcional) Copiar config.example.json -> config.json y editar tu IP

CONCEPTOS CLAVE:
    - Protocolo TCP: 4 bytes de tamaño + datos JPEG
    - Context manager `with`: conexión automática
    - Bucle infinito para streaming continuo
    - `cv2.waitKey()` para controles de teclado

CASOS DE USO:
    - Verificar que el sistema funciona
    - Monitoreo básico en tiempo real
    - Base para aplicaciones más complejas
    - Debugging visual del servidor

TIEMPO ESTIMADO: 10 minutos

DETENER: Pulsa `q` en la ventana para salir
=============================================================================
"""

import argparse
import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config_loader import load_config

from rpicam_tcp_client import CameraClient


def main():
    """
    Función principal: conecta, recibe frames y los muestra hasta presionar 'q'.

    Flujo del programa:
        1. Cargar config.json (si existe)
        2. Parsear argumentos (--host, --port)
        3. Crear CameraClient con valores por defecto del servidor
        4. Conectar con `with` (automático disconnect)
        5. Bucle infinito: get_frame() → cv2.imshow() → waitKey()
        6. Salir limpiamente al presionar 'q'
    """
    # =========================================================================
    # PASO 1: Cargar configuración desde config.json (si existe)
    # =========================================================================
    # load_config() busca config.json en la raiz del proyecto
    # Si no existe, devuelve {} y los argumentos de la linea de comandos
    # o lo svalores por defecto del argparse se usarán
    cfg = load_config()
    cfg_conexion = cfg.get("conexion", {})

    # =========================================================================
    # PASO 2: Parsear argumentos de línea de comandos
    # =========================================================================
    # Los argumentos de terminal SIEMPRE tiene prioridad sobre config.json
    # Si no se pasa --host, se usa el valor del config.json o falla con error
    parser = argparse.ArgumentParser(
        description="Muestra vídeo desde la Raspberry Pi (valores por defecto)."
    )
    parser.add_argument(
        "--host", default=cfg_conexion.get("host"), help="IP de la Raspberry Pi"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=cfg_conexion.get("port", 5001),
        help="Puerto TCP (por defecto 5001)",
    )
    args = parser.parse_args()

    if args.host is None:
        print("Error: indica --host o configura 'host' en config.json")
        sys.exit(1)

    msg = f"Conectando a {args.host}:{args.port}. Valores por defecto del servidor."
    print(msg)

    # =========================================================================
    # PASO 3: Crear CameraClient — Valores por defecto del servidor
    # =========================================================================
    cam = CameraClient(
        host=args.host,
        port=args.port,
        # No especificamos más parámetros -> servidor usa por defecto
    )
    # =========================================================================
    # PASO 4: Conectar con Context Manager (automático disconnect)
    # =========================================================================
    with cam:
        print("Recibiendo video. Pulsa 'q' para salir.")

        # =====================================================================
        # PASO 4.1: Bucle infinito de streaming
        # =====================================================================
        # while True continúa hasta que:
        # - Usuario pulse 'q' (cv2.waitKey detecta ord('q'))
        # - Conexión perdida (get_frame() retorna None)

        while True:
            # -----------------------------------------------------------------
            # 4.2: Recibir frame del servidor
            # -----------------------------------------------------------------
            # get_frame() lee el protocolo TCP:
            # 1. 4 bytes con tamaño del JPEG
            # 2. N bytes del frame comprimido
            # 3. Decodifica con cv2.imdecode()
            # 4. Convierte RGB→BGR para OpenCV
            frame = cam.get_frame()

            if frame is None:
                print("Conexión perdida")
                break

            # -----------------------------------------------------------------
            # 4.3: Mostrar frame en ventana
            # -----------------------------------------------------------------
            # cv2.imshow crea/mantiene ventana con nombre "Raspberry Pi Camera".
            # OpenCV maneja buffers y refresco automático.

            cv2.imshow("RaspberryPi CAM", frame)

            # -----------------------------------------------------------------
            # 4.4: Esperar tecla (1ms timeout = no bloquea)
            # -----------------------------------------------------------------
            # cv2.waitKey(1) espera máximo 1ms por tecla.
            # & 0xFF elimina bits altos (cross-platform).
            # ord('q') = 113 → sale limpiamente.

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break

    # =========================================================================
    # PASO 5: Limpiar ventanas OpenCV (automático por with)
    # =========================================================================
    # cv2.destroyAllWindows() cierra todas las ventanas abiertas.
    # El `with cam:` ya desconectó el cliente.

    cv2.destroyAllWindows()
    print("Ejemplo completado exitosamente.")


# =============================================================================
# EJERCICIOS PARA PRACTICAR:
# =============================================================================
#
# 1. **BÁSICO**: Añade `--fps` para mostrar FPS real cada 30 frames.
#    Pista: `time.time()` + contador.
#
# 2. **INTERMEDIO**: Captura teclas `+`/`-` para zoom dinámico.
#    Pista: `cv2.resize(frame, nuevo_tamaño)` dentro del bucle.
#
# 3. **AVANZADO**: Añade detección de movimiento básica (diferencia frame anterior).
#    Imprime "MOVIMIENTO DETECTADO" en consola.
#
# 4. **INVESTIGACIÓN**: Mide latencia real (timestamp servidor vs cliente).
#    Pide al servidor que añada timestamp al frame.
#
# 5. **VISUALIZACIÓN**: Superpone texto con FPS y parámetros actuales.
#    Pista: `cv2.putText(frame, "FPS: 30", ...)`
#
# =============================================================================

if __name__ == "__main__":
    main()
