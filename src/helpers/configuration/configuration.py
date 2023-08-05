from typing import Any, Dict
import os

class Configuration:
    _instance = None
    _config: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Configuration, cls).__new__(cls)
            cls._config = cls.load_config()
        return cls._instance

    @classmethod
    def load_env(cls, file_path=".env"):
        env_vars = {}

        if not os.path.exists(file_path):
            # If .env does not exist, copy from .env.example
            with open('.env.example', 'r') as source_file, open(file_path, 'w') as dest_file:
                for line in source_file:
                    dest_file.write(line)

        with open(file_path, "r", encoding="utf-8") as env_file:
            for line in env_file:
                key, value = line.strip().split("=", 1)
                env_vars[key] = value

        return env_vars

    @classmethod
    def load_config(cls) -> Dict[str, Any]:
        config: Dict[str, Any] = cls.read_config()
        cls.validate_config(config)
        print("Configuration is valid.")
        return config

    @classmethod
    def read_config(cls) -> Dict[str, Any]:
        env_vars = cls.load_env()

        config: Dict[str, Any] = {
            "API_POST_URL": env_vars.get("API_POST_URL"),
            "API_TOKEN": env_vars.get("API_TOKEN"),
            "API_ENABLED": env_vars.get("API_ENABLED") == "true",
            "LOGGING_LEVEL": env_vars.get("LOGGING_LEVEL"),
            "LOGGING_ENABLED": env_vars.get("LOGGING_ENABLED") == "true",
            "SERVICE_HTTP_ENABLED": env_vars.get("SERVICE_HTTP_ENABLED") == "true",
            "SERVICE_SSH_ENABLED": env_vars.get("SERVICE_SSH_ENABLED") == "true"
        }

        try:
            config["SERVICE_HTTP_PORT"] = int(env_vars.get("SERVICE_HTTP_PORT"))
        except ValueError:
            config["SERVICE_HTTP_PORT"] = None

        try:
            config["SERVICE_SSH_PORT"] = int(env_vars.get("SERVICE_SSH_PORT"))
        except ValueError:
            config["SERVICE_SSH_PORT"] = None

        return config

    @classmethod
    def validate_api_post_url(cls, value):
        if value is None:
            raise ValueError("Missing API_POST_URL in the environment variables.")

    @classmethod
    def validate_api_token(cls, value):
        if value is None:
            raise ValueError("Missing API_TOKEN in the environment variables.")

    @classmethod
    def validate_boolean(cls, value, key):
        if not isinstance(value, bool):
            raise ValueError(f"'{key}' should be a boolean.")

    @classmethod
    def validate_integer(cls, value, key):
        if not isinstance(value, int):
            raise ValueError(f"'{key}' should be an integer.")

    @classmethod
    def validate_config(cls, config: Dict[str, Any]) -> None:
        cls.validate_api_post_url(config.get("API_POST_URL"))
        cls.validate_api_token(config.get("API_TOKEN"))
        cls.validate_boolean(config.get("API_ENABLED"), "API_ENABLED")
        cls.validate_boolean(config.get("LOGGING_ENABLED"), "LOGGING_ENABLED")
        cls.validate_boolean(config.get("SERVICE_HTTP_ENABLED"), "SERVICE_HTTP_ENABLED")
        cls.validate_boolean(config.get("SERVICE_SSH_ENABLED"), "SERVICE_SSH_ENABLED")
        cls.validate_integer(config.get("SERVICE_HTTP_PORT"), "SERVICE_HTTP_PORT")
        cls.validate_integer(config.get("SERVICE_SSH_PORT"), "SERVICE_SSH_PORT")

    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        if cls._config is None:
            cls._config = cls.load_config()
        return cls._config

    @classmethod
    def set_config_item(cls, key, value):
        if cls._config is None:
            cls._config = cls.load_config()
        cls._config[key] = value
