from pydantic import BaseModel


class Route:
    id: int
    agency_id: int
    short_name: str
    long_name: str
    description: str
    type: str
    color: str


