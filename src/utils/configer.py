import os
from pathlib import Path
from typing import Any, List, Dict

from dotenv import load_dotenv


class Configer:

    def __init__(self):
        self._config: Dict[str, Any] = {}
        self._defaults: Dict[str, Any] = {}
        self._load_configuration()

    def get(self, key: str, default: Any = None, required: bool = False) -> Any:
        env_value = os.getenv(key)
        if env_value is not None:
            return self._convert_value(env_value)

        if key in self._config:
            return self._config[key]

        if key in self._defaults:
            return self._defaults[key]

        if default is not None:
            return default

        if required:
            raise ValueError(f"Required configuration key '{key}' not found")

        return None

    def list(self) -> List[str]:
        keys = set()

        keys.update(os.environ.keys())

        keys.update(self._config.keys())

        keys.update(self._defaults.keys())

        return sorted(list(keys))

    def _load_configuration(self):
        env_file = Path('.env')
        if env_file.exists():
            load_dotenv(env_file)

        if env_file.exists():
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")
                            self._config[key] = self._convert_value(value)
            except UnicodeDecodeError:
                # If UTF-8 fails, try with system default encoding
                try:
                    with open(env_file, 'r', encoding='latin-1') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#') and '=' in line:
                                key, value = line.split('=', 1)
                                key = key.strip()
                                value = value.strip().strip('"').strip("'")
                                self._config[key] = self._convert_value(value)
                except Exception:
                    # If all encoding attempts fail, skip the file
                    pass

        self._defaults.update({
            'LOG_LEVEL': 'INFO',
            'LOG_FORMAT': 'json',
            'CONFIG_ENV': 'development'
        })

    def _convert_value(self, value: str) -> Any:
        if not isinstance(value, str):
            return value

        # Convert boolean strings including numeric representations
        lower_value = value.lower()
        if lower_value in ('true', 'yes', 'on', '1'):
            return True
        if lower_value in ('false', 'no', 'off', '0'):
            return False

        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            pass

        return value