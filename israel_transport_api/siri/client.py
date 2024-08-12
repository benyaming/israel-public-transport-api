import logging
from datetime import datetime as dt

from pydantic import parse_obj_as
from httpx import ReadTimeout
from psycopg.connection_async import AsyncConnection

from israel_transport_api.config import env
from israel_transport_api.gtfs.repository import routes_repository, stops_repository
from israel_transport_api.misc import http_client
from israel_transport_api.siri.exceptions import SiriException
from israel_transport_api.siri.models import IncomingRoute, IncomingRoutesResponse
from israel_transport_api.siri.siri_models import MonitoredStopVisit, VehicleLocation

RETRY_COUNT = 5
logger = logging.getLogger('siri_client')


async def _make_request(stop_code: int, monitoring_interval: int, retry_count: int = 0) -> list[MonitoredStopVisit]:
    params = {
        'Key': env.API_KEY,
        'MonitoringRef': stop_code,
        'PreviewInterval': f'PT{monitoring_interval}M'
    }

    try:
        resp = await http_client.get(env.SIRI_URL, params=params)
    except ReadTimeout:
        logger.error('Read timeout!')
        if retry_count < RETRY_COUNT:
            raise
        return await _make_request(stop_code, monitoring_interval, retry_count + 1)

    raw_data: dict = resp.json()
    raw_stop_data: list[dict] = raw_data.get('Siri', {}).get('ServiceDelivery', {}).get('StopMonitoringDelivery', [])

    if len(raw_stop_data) == 0:
        raise SiriException('No data received', 3)

    if raw_stop_data[0]['Status'] != 'true':
        message = raw_stop_data[0].get('ErrorCondition', {}).get('Description')
        raise SiriException(message, 1)

    parsed_data = parse_obj_as(list[MonitoredStopVisit], raw_stop_data[0]['MonitoredStopVisit'])  # currently support for one stop code
    return parsed_data


async def get_incoming_routes(
        conn: AsyncConnection,
        stop_code: int,
        monitoring_interval: int = 30
) -> IncomingRoutesResponse:
    siri_data = await _make_request(stop_code, monitoring_interval)
    stop_info = await stops_repository.find_stop_by_code(stop_code, conn)

    incoming_routes: list[IncomingRoute] = []
    for stop_visit in siri_data:
        arrival_time = stop_visit.monitored_vehicle_journey.monitored_call.expected_arrival_time.replace(tzinfo=None)
        eta = (arrival_time - dt.now()).seconds // 60
        route = await routes_repository.find_route_by_id(int(stop_visit.monitored_vehicle_journey.line_ref), conn)
        incoming_routes.append(
            IncomingRoute(
                eta=eta,
                route=route,
                plate_number=stop_visit.monitored_vehicle_journey.vehicle_ref
            )
        )

    resp = IncomingRoutesResponse(stop_info=stop_info, incoming_routes=sorted(incoming_routes, key=lambda r: r.eta))
    return resp


async def get_vehicle_location(vehicle_plate_number: str, stop_code: int) -> VehicleLocation:
    siri_data = await _make_request(stop_code, 30)
    vehicle = list(
        filter(
            lambda m: m.monitored_vehicle_journey.vehicle_ref == vehicle_plate_number,
            siri_data
        )
    )
    if len(vehicle) == 0:
        raise ValueError  # todo
    current_location = vehicle[0].monitored_vehicle_journey.vehicle_location
    return current_location
