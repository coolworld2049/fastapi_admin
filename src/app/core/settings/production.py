from app.core.settings.app import AppSettings


class ProdAppSettings(AppSettings):
    class Config(AppSettings.Config):
        env_file = "prod.env"
        env_file_encoding = 'utf-8'
