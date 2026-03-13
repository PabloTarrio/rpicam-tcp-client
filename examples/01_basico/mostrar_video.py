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

import cv2

from rpicam_tcp_client import CameraClient


def main():
    """
    Función principal: conecta, recibe frames y los muestra hasta presionar 'q'.

    Flujo del programa:
        1. Parsear argumentos (--host, --port)
        2. Crear CameraClient con valores por defecto del servidor
        3. Conectar con `with` (automático disconnect)
        4. Bucle infinito: get_frame() → cv2.imshow() → waitKey()
        5. Salir limpiamente al presionar 'q'
    """

    # =========================================================================
    # PASO 1: Parsear argumentos de línea de comandos
    # =========================================================================
    # argparse permite usar --host y --port desde terminal.
    # Valores por defecto aseguran que funcione sin parámetros extra.

    parser = argparse.ArgumentParser(
        description="Muestra vídeo desde la Raspberry Pi (valores por defecto)."
    )
    parser.add_argument("--host", required=True, help="IP de la Raspberry Pi")
    parser.add_argument(
        "--port", type=int, default=5001, help="Puerto TCP (por defecto 5001)"
    )
    args = parser.parse_args()

    msg = f"Conectando a {args.host}:{args.port}. Valores por defecto del servidor."
    print(msg)

    # =========================================================================
    # PASO 2: Crear CameraClient — Valores por defecto del servidor
    # =========================================================================
    # Al NO pasar parámetros, CameraClient envía {} vacío al servidor.
    # El servidor usa: 1920x1080, JPEG=80, controles neutros.

    cam = CameraClient(
        host=args.host,
        port=args.port,
        # No especificamos más parámetros -> servidor usa por defecto
    )
    # =========================================================================
    # PASO 3: Conectar con Context Manager (automático disconnect)
    # =========================================================================
    # `with` garantiza que cam.disconnect() se llame SIEMPRE,
    # incluso si hay excepciones o el usuario cierra abruptamente.

    with cam:
        print("Recibiendo video. Pulsa 'q' para salir.")

        # =====================================================================
        # PASO 4: Bucle infinito de streaming
        # =====================================================================
        # while True continúa hasta que:
        # - Usuario pulse 'q' (cv2.waitKey detecta ord('q'))
        # - Conexión perdida (get_frame() retorna None)

        while True:
            # -----------------------------------------------------------------
            # 4.1: Recibir frame del servidor
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
            # 4.2: Mostrar frame en ventana
            # -----------------------------------------------------------------
            # cv2.imshow crea/mantiene ventana con nombre "Raspberry Pi Camera".
            # OpenCV maneja buffers y refresco automático.

            cv2.imshow("RaspberryPi CAM", frame)

            # -----------------------------------------------------------------
            # 4.3: Esperar tecla (1ms timeout = no bloquea)
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
