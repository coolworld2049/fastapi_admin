from enum import Enum

from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()


class AppEnvTypes(Enum):
    prod: str = "prod"
    dev: str = "dev"
    test: str = "tests"


class BaseAppSettings(BaseSettings):
    app_env: AppEnvTypes = AppEnvTypes.prod

    class Config:
        env_file = ".env"
