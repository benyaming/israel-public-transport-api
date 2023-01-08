from pydantic import BaseSettings, Field


class Env(BaseSettings):

    class Config:
        env_file = '../.env'
        env_file_encoding = 'utf-8'

    SIRI_URL: str = Field(..., env='SIRI_URL')
    GTFS_URL: str = Field(..., env='GTFS_URL')
    API_KEY: str = Field(..., env='API_KEY')
    ROOT_PATH: str = Field('', env='ROOT_PATH')
    DB_URL: str = Field('localhost', env='DB_URL')
    DB_NAME: str = Field(..., env='DB_NAME')
    SCHED_HOURS: int = Field(..., env='SCHED_HOURS')
    SCHED_MINS: int = Field(..., env='SCHED_MINS')


env = Env()
