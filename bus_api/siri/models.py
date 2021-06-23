from __future__ import annotations
from datetime import datetime, date
from typing import Optional, List

from pydantic import BaseModel, Field


# TODO - documentation and comments!


# class SiriResponse(BaseModel):
#     ...
#
#     class Config:
#         @classmethod
#         def alias_generator(cls, string: str) -> str:
#             return ''.join(word.capitalize() for word in string.split('_'))
#
#
# class ServiceDelivery(BaseModel):
#     stop_monitoring_delivery: StopMonitoringDelivery


class StopMonitoringDelivery(BaseModel):
    status: str  # = Field(alias='Status')
    monitored_stop_visit: List[MonitoredStopVisit]  # = Field(alias='MonitoredStopVisit')

    class Config:
        @classmethod
        def alias_generator(cls, string: str) -> str:
            return ''.join(word.capitalize() for word in string.split('_'))


class MonitoredStopVisit(BaseModel):
    """

    """
    item_identifier: str  # = Field(alias='ItemIdentifier')
    monitoring_ref: str  # = Field(alias='MonitoringRef')
    monitored_vehicle_journey: MonitoredVehicleJourney  # = Field(alias='MonitoredVehicleJourney')


class MonitoredVehicleJourney(BaseModel):
    """

    """
    published_line_name: str  # = Field(alias='PublishedLineName')
    line_ref: str  # = Field(alias='LineRef')
    direction_ref: str  # = Field(alias='DirectionRef')
    operator_ref: str  # = Field(alias='OperatorRef')
    destination_ref: str  # = Field(alias='DestinationRef')
    vehicle_ref: str  # = Field(alias='VehicleRef')
    framed_vehicle_journey_ref: FramedVehicleJourneyRef  # = Field(alias='FramedVehicleJourneyRef')
    vehicle_location: VehicleLocation  # = Field(alias='VehicleLocation')
    monitored_call: MonitoredCall  # = Field(alias='MonitoredCall')


class FramedVehicleJourneyRef(BaseModel):
    """

    """
    data_frame_ref: date  # = Field(alias='DataFrameRef')
    dated_vehicle_journey_ref: str  # = Field(alias='DatedVehicleJourneyRef')


class VehicleLocation(BaseModel):
    """

    """
    latitude: float  # = Field(alias='Latitude')
    longitude: float  # = Field(alias='Longitude')


class MonitoredCall(BaseModel):
    """

    """
    stop_point_ref: str  # = Field(alias='StopPointRef')
    order: str  # = Field(alias='Order')
    aimed_arrival_time: Optional[datetime]  # = Field(alias='AimedArrivalTime')
    expected_arrival_time: datetime  # = Field(alias='ExpectedArrivalTime')
    arrival_status: Optional[str]  # = Field(alias='ArrivalStatus')
    arrival_platform_name: Optional[str]  # = Field(alias='ArrivalPlatformName')
