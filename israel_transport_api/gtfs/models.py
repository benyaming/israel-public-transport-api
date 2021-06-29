from dataclasses import dataclass


@dataclass
class Route:
    id: str
    agency_id: str
    short_name: str
    from_stop_name: str
    to_stop_name: str
    from_city: str
    to_city: str
    description: str
    type: str
    color: str


