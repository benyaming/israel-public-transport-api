from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from israel_transport_api.gtfs.models import Stop, Route


class IncomingRoutesResponse(BaseModel):
    response_time: datetime = Field(default_factory=datetime.now)
    stop_info: Stop
    incoming_routes: List['IncomingRoute']


class IncomingRoute(BaseModel):
    eta: int
    route: Route


IncomingRoutesResponse.update_forward_refs()
