from pydantic_settings import BaseSettings, SettingsConfigDict


class Env(BaseSettings):

    model_config = SettingsConfigDict(env_file='../.env', env_file_encoding='utf-8')

    SIRI_URL: str
    GTFS_URL: str
    API_KEY: str
    ROOT_PATH: str = '/'
    DB_DSN: str
    SCHED_HOURS: int
    SCHED_MINS: int

    DB_BATCH_SIZE: int = 300_000


env = Env()
