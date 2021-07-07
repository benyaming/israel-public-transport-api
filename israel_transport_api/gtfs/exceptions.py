from fastapi import HTTPException
from pydantic import BaseModel


class GtfsFileNotFound(Exception):
    pass


class StopNotFound(Exception):
    def __init__(self, stop_code):
        raise HTTPException(422, {'message': f'Stop with code [{stop_code}] not found!', 'code': 1})


class RouteNotFound(Exception):
    def __init__(self, stop_code):
        raise HTTPException(422, {'message': f'Route with id [{stop_code}] not found!', 'code': 2})


