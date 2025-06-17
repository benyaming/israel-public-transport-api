from fastapi import HTTPException


class SiriException(Exception):
    def __init__(self, message: str, code: int, status_code: int = 400):
        raise HTTPException(status_code, {'message': message, 'code': code})

