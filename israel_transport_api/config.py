import json
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict, NoDecode


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
    # "host:*" port wildcards). Empty/unset (default) disables the check, which is
    # appropriate when the service runs behind a reverse proxy. Provide values as a
    # JSON array, e.g. MCP_ALLOWED_HOSTS='["example.com", "localhost:*"]'.
    MCP_ALLOWED_HOSTS: Annotated[list[str], NoDecode] = Field(default_factory=list)
    MCP_ALLOWED_ORIGINS: Annotated[list[str], NoDecode] = Field(default_factory=list)

    @field_validator('MCP_ALLOWED_HOSTS', 'MCP_ALLOWED_ORIGINS', mode='before')
    @classmethod
    def _parse_host_list(cls, v):
        # NoDecode hands us the raw env string; treat blank as "no allow-list" rather
        # than letting an empty value blow up JSON parsing.
        if isinstance(v, str):
            v = v.strip()
            return json.loads(v) if v else []
        return v


env = Env()
