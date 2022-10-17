from datetime import datetime

from pydantic import BaseModel, Field

from israel_transport_api.gtfs.models import Stop, Route
from israel_transport_api.siri.siri_models import VehicleLocation


class IncomingRoutesResponse(BaseModel):
    response_time: datetime = Field(default_factory=datetime.now)
    stop_info: Stop
    incoming_routes: list['IncomingRoute']


class IncomingRoute(BaseModel):
    eta: int
    plate_number: str
    route: Route


class VehicleLocationResponse(BaseModel):
    latitude: float
    longitude: float

    @classmethod
    def from_siri_model(cls, siri_model: VehicleLocation):
        return cls(
            latitude=siri_model.latitude,
            longitude=siri_model.longitude
        )


IncomingRoutesResponse.update_forward_refs()
