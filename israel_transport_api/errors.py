from pydantic import BaseModel


class ErrorCode:
    stop_not_found: 1
    route_not_found: 2


class Error(BaseModel):
    code: int
    message: str


class ApiException(Exception, BaseModel):
    code: int
    message: str
