"""
config_loader.py - Cargador de configuración gloabl para los ejemplos.

Busca config.json en la raiz del proyecto. Si no existe, devuelve un
diccionario vacío y cada script usará sus valores por defecto.

Uso en cualquier script de examples/:
    from config_loader import load_config
    cfg = load_config()
    host = cfg.get("conexion",{}).get("host","192.168.1.100")
"""

import json
from pathlib import Path

# Variable de módulo: permite hacer patch en los tests
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"


def load_config() -> dict:
    """
    Carga config.json desde la raiz del proyecto.

    Returns:
        dict: Contenido del archivo de configuración,
            o diccionario vacío si no existe o tiene JSON inválido.
    """
    if not CONFIG_PATH.exists():
        return {}

    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}
