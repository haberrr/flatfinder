import os
from typing import Tuple, Union, Any

import yaml

CONFIG_PATH = os.getenv('FLATFINDER_CONFIG', os.path.expanduser('~/.config/flatfinder/config.yaml'))


class _YamlConfig:
    def __init__(self, config=None):
        self.config = config

    def __getitem__(self, key: Union[str, Tuple]) -> Any:
        if isinstance(key, tuple):
            item = self.config
            for part in key:
                if isinstance(item, dict):
                    item = item.get(part, {})
                elif isinstance(item, list):
                    try:
                        item = item[int(part)]
                    except (IndexError, ValueError):
                        return None
                else:
                    return None
            return item if item else None
        elif key in self.config:
            return self.config[key]
        else:
            return self[tuple(key.split('.'))]

    @classmethod
    def from_file(cls, file):
        if os.path.exists(file):
            with open(file) as f:
                config = yaml.safe_load(f)

        return cls(config)


class Settings:
    _config = _YamlConfig.from_file(CONFIG_PATH)

    DB_HOST = os.environ.get('FLATFINDER_DB_HOST', _config['mongodb.host'])
    DB_PORT = os.environ.get('FLATFINDER_DB_PORT', _config['mongodb.port'])
    DB_DBNAME = os.environ.get('FLATFINDER_DB_NAME', _config['mongodb.db_name'])
    DB_USER = os.environ.get('FLATFINDER_DB_USER', _config['mongodb.user'])
    DB_PWD = os.environ.get('FLATFINDER_DB_PASSWORD', _config['mongodb.password'])

    TG_BOT_TOKEN = os.environ.get('FLATFINDER_BOT_TOKEN', _config['telegram.bot_token'])
    TG_CHAT_IDS = os.environ.get('FLATFINDER_CHAT_IDS', _config['telegram.chat_ids'])
