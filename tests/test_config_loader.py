"""
Tests unitarios para config_loader.load_config()

usamos tmp_path (fixture de pytest) para crear archivos
temporales sin tocar el proyecto real
"""

import json
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "examples"))

from config_loader import load_config


# ==============================================================================
# TEST: load_config()
# ==============================================================================
class TestLoadConfig:
    def test_config_valida_devuelve_dict(self, tmp_path):
        config_data = {
            "conexion": {"host": "192.168.1.1", "port": 5001},
            "camara": {"width": 640, "height": 480},
        }

        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(config_data))

        with patch("config_loader.CONFIG_PATH", config_file):
            result = load_config()

        assert result["conexion"]["host"] == "192.168.1.1"
        assert result["camara"]["width"] == 640

    def test_config_no_existe_devuelve_dict_vacio(self, tmp_path):
        ruta_inexistente = tmp_path / "no_existe.json"

        with patch("config_loader.CONFIG_PATH", ruta_inexistente):
            result = load_config()

        assert result == {}

    def test_config_json_invalido_devuelve_dict_vacio(self, tmp_path):
        config_file = tmp_path / "config.json"
        config_file.write_text("esto no es json {{{")

        with patch("config_loader.CONFIG_PATH", config_file):
            result = load_config()

        assert result == {}

    def test_config_vacia_devuelve_dict_vacio(self, tmp_path):
        config_file = tmp_path / "config.json"
        config_file.write_text("{}")

        with patch("config_loader.CONFIG_PATH", config_file):
            result = load_config()

        assert result == {}

    def test_subsecciones_accesibles(self, tmp_path):
        config_data = {
            "grabacion": {"fps": 25, "duration": 60},
            "calibracion": {"tablero_cols": 9, "tablero_rows": 6},
        }
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(config_data))

        with patch("config_loader.CONFIG_PATH", config_file):
            result = load_config()

        assert result.get("grabacion", {}).get("fps") == 25
        assert result.get("calibracion", {}).get("tablero_cols") == 9
