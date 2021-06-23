from __future__ import annotations
from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, Field


class SiriResponse(BaseModel):
    ...


class MonitoredStopVisit(BaseModel):
    """

    """
    item_identifier: str = Field(alias='ItemIdentifier')
    monitoring_ref: str = Field(alias='MonitoringRef')


class FramedVehicleJourneyRef(BaseModel):
    """

    """
    data_frame_ref: date = Field(alias='DataFrameRef')
    dated_vehicle_journey_ref: str = Field(alias='DatedVehicleJourneyRef')


class MonitoredVehicleJourney(BaseModel):
    """

    """
    ...


class VehicleLocation(BaseModel):
    """

    """
    latitude: float = Field(alias='Latitude')
    longitude: float = Field(alias='Longitude')


class MonitoredCall(BaseModel):
    """

    """
    stop_point_ref: str = Field(alias='StopPointRef')
    order: str = Field(alias='Order')
    aimed_arrival_time: Optional[datetime] = Field(alias='AimedArrivalTime')
    expected_arrival_time: datetime = Field(alias='ExpectedArrivalTime')
    arrival_status: Optional[str] = Field(alias='ArrivalStatus')
    arrival_platform_name: Optional[str] = Field(alias='ArrivalPlatformName')
