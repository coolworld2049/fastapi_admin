from enum import Enum

from dotenv import load_dotenv
from pydantic import BaseSettings
from pydantic.env_settings import SettingsSourceCallable

load_dotenv()


class AppEnvTypes(Enum):
    prod: str = "prod"
    dev: str = "dev"
    test: str = "test"


class BaseAppSettings(BaseSettings):
    app_env: AppEnvTypes = AppEnvTypes.prod

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = 'utf-8'

        @classmethod
        def customise_sources(
                cls,
                init_settings: SettingsSourceCallable,
                env_settings: SettingsSourceCallable,
                file_secret_settings: SettingsSourceCallable,
        ) -> tuple[SettingsSourceCallable, ...]:
            return env_settings, init_settings, file_secret_settings
