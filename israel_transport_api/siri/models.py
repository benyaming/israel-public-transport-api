from datetime import datetime

from pydantic import BaseModel, Field

from israel_transport_api.gtfs.models import Stop, Route


class IncomingRoutesResponse(BaseModel):
    response_time: datetime = Field(default_factory=datetime.now)
    stop_info: Stop
    incoming_routes: list['IncomingRoute']


class IncomingRoute(BaseModel):
    eta: int
    route: Route


IncomingRoutesResponse.update_forward_refs()
