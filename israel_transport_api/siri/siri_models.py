from __future__ import annotations

from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel


class BaseModelPascal(BaseModel):
    class Config:

        @classmethod
        def alias_generator(cls, string: str) -> str:
            return ''.join(word.capitalize() for word in string.split('_'))


class MonitoredStopVisit(BaseModelPascal):
    """
    Describes a response with set of arriving lines to the station.
    """
    item_identifier: str  # Unique identifier of the MonitoredStopVisit.
    monitoring_ref: str  # The monitored stop code.
    monitored_vehicle_journey: MonitoredVehicleJourney


class MonitoredVehicleJourney(BaseModelPascal):
    """
    Describes one arriving vehicle item.
    """
    published_line_name: str  # The line number, as published on the vehicle like (561, 7, א99). The value is reference to route_short_name at the GTFS.
    line_ref: str  # GTFS ref to line.
    direction_ref: str  # GTFS ref to direction.
    operator_ref: str  # GTFS ref to operator.
    destination_ref: str  # GTFS ref to destination.
    vehicle_ref: str  # Vehicle's license plate number
    framed_vehicle_journey_ref: FramedVehicleJourneyRef  # class for GTFS ref trip_id.
    vehicle_location: Optional[VehicleLocation]  # class for vehicle current location.
    monitored_call: MonitoredCall  # class for vehicle's predicted arrival time.


class FramedVehicleJourneyRef(BaseModelPascal):
    """
    Describes GTFS's trip_id
    """
    data_frame_ref: date  # date of GTFS data frame.
    dated_vehicle_journey_ref: str  # ref to route_short_name at the GTFS.


class VehicleLocation(BaseModelPascal):
    """
    Describes vehicle's current location.
    """
    latitude: float
    longitude: float


class MonitoredCall(BaseModelPascal):
    """
    Describes expected vehicle arrival time, predicted by SIRI server
    """
    stop_point_ref: Optional[str]  # stop_id in GTFS. Usually the same as passed to request.
    order: Optional[str]  # Monitored stop order. The first stop is at order 1
    aimed_arrival_time: Optional[datetime]  # Planned arrival time to the Monitored stop. The value will be pass only when the Vehicle have not started the journey.
    expected_arrival_time: Optional[datetime]  # Expected arrival time to the Monitored stop.
    arrival_platform_name: Optional[str]  # Arrival platform name, mainly for trains.


MonitoredStopVisit.update_forward_refs()
MonitoredVehicleJourney.update_forward_refs()
FramedVehicleJourneyRef.update_forward_refs()
VehicleLocation.update_forward_refs()
MonitoredCall.update_forward_refs()

