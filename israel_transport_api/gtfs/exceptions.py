from fastapi import HTTPException


class GtfsFileNotFound(Exception):
    pass


class StopNotFound(Exception):
    def __init__(self, stop_code):
        msg = f'Stop with code [{stop_code}] not found!'
        raise HTTPException(404, msg)


class RouteNotFound(Exception):
    def __init__(self, stop_code):
        msg = f'Route with id [{stop_code}] not found!'
        raise HTTPException(404, msg)
