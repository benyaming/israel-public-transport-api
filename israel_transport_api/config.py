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

    WS_UPDATE_INTERVAL: int = 5

    # MCP DNS-rebinding protection. When MCP_ALLOWED_HOSTS is non-empty, the mounted
    # /mcp endpoint validates the Host header against this allow-list (supports
    # "host:*" port wildcards). Empty (default) disables the check, which is
    # appropriate when the service runs behind a reverse proxy. Provide values as a
    # JSON array, e.g. MCP_ALLOWED_HOSTS='["example.com", "localhost:*"]'.
    MCP_ALLOWED_HOSTS: list[str] = []
    MCP_ALLOWED_ORIGINS: list[str] = []


env = Env()
