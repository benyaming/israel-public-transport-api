from abc import ABC
from typing import Optional, Tuple
from dataclasses import dataclass

from odmantic import Field, Model, EmbeddedModel


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


class StopLocation(EmbeddedModel, ABC):
    type: str = 'Point'
    coordinates: Tuple[float, float]


class Stop(Model, ABC):
    id: int = Field(..., primary_field=True)
    code: int
    name: str
    city: str
    street: Optional[str] = None
    floor: Optional[str] = None
    platform: Optional[str] = None
    location: StopLocation
    location_type: str
    parent_station_id: Optional[str] = None
    zone_id: Optional[str] = None

    class Config:
        collection = 'stops'

        schema_extra = {
            'example': {
                'id': 10846,
                'code': 5200,
                'name': 'בנייני האומה',
                'city': 'ירושלים',
                'street': 'שדרות שז''ר',
                'floor': None,
                'platform': None,
                'location': {
                    'type': 'Point',
                    'coordinates': [31.787909, 35.203428]
                },
                'location_type': '0',
                'parent_station_id': '',
                'zone_id': '3000'
            }
        }
