import logging
from datetime import datetime as dt
from typing import List

from pydantic import parse_obj_as

from israel_transport_api.config import SIRI_URL, API_KEY
from israel_transport_api.gtfs.repository import routes_repository, stops_repository
from israel_transport_api.misc import http_client
from israel_transport_api.siri.models import IncomingRoute, IncomingRoutesResponse
from israel_transport_api.siri.siri_models import MonitoredStopVisit

logging.basicConfig(level=logging.DEBUG)


async def _make_request(stop_code: int, monitoring_interval: int) -> List[MonitoredStopVisit]:
    params = {
        'Key': API_KEY,
        'MonitoringRef': stop_code,
        'PreviewInterval': f'PT{monitoring_interval}M'
    }

    resp = await http_client.get(SIRI_URL, params=params)
    raw_data: dict = resp.json()
    raw_stop_data: List[dict] = raw_data.get('Siri', {}).get('ServiceDelivery', {}).get('StopMonitoringDelivery', [])

    if len(raw_stop_data) == 0:
        print('no data')
        raise ValueError()

    if raw_stop_data[0]['Status'] != 'true':
        print('error', raw_stop_data)
        raise ValueError()

    parsed_data = parse_obj_as(List[MonitoredStopVisit], raw_stop_data[0]['MonitoredStopVisit'])  # currently support for one stop code
    return parsed_data


async def get_incoming_routes(stop_code: int, monitoring_interval: int = 30) -> IncomingRoutesResponse:
    siri_data = await _make_request(stop_code, monitoring_interval)
    stop_info = await stops_repository.find_stop_by_code(stop_code)

    incoming_routes: List[IncomingRoute] = []
    for stop_visit in siri_data:
        arrival_time = stop_visit.monitored_vehicle_journey.monitored_call.expected_arrival_time.replace(tzinfo=None)
        eta = (arrival_time - dt.now()).seconds // 60
        route = routes_repository.find_route_by_id(stop_visit.monitored_vehicle_journey.line_ref)
        incoming_routes.append(IncomingRoute(eta=eta, route=route))

    resp = IncomingRoutesResponse(stop_info=stop_info, incoming_routes=sorted(incoming_routes, key=lambda r: r.eta))
    return resp
