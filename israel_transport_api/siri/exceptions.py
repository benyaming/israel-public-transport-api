from fastapi import HTTPException


class SiriException(Exception):
    def __init__(self, message: str, code: int):
        raise HTTPException(422, {'message': message, 'code': code})

