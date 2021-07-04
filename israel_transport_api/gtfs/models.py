from abc import ABC
from typing import Optional, Tuple
from dataclasses import dataclass

from odmantic import Model, EmbeddedModel


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


class Stop(Model, ABC):
    stop_id: str
    code: str
    name: str
    city: str
    street: Optional[str] = None
    floor: Optional[str] = None
    platform: Optional[str] = None
    location: 'StopLocation'
    location_type: str
    parent_station_id: Optional[str] = None
    zone_id: Optional[str] = None

    class Config:
        collection = 'stops'


class StopLocation(EmbeddedModel, ABC):
    type: str = 'Point'
    coordinates: Tuple[float, float]


Stop.update_forward_refs()
