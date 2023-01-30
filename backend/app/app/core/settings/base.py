import os
from enum import Enum

from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()


class AppEnvTypes(Enum):
    prod: str = "prod"
    dev: str = "dev"
    test: str = "test"


class BaseAppSettings(BaseSettings):
    APP_ENV: str = os.getenv("APP_ENV", AppEnvTypes.prod)
    assert APP_ENV in [x.name for x in AppEnvTypes], ValueError()
    app_env: AppEnvTypes = APP_ENV

    class Config:
        env_file = ".env"
