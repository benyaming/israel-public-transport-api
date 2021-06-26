import logging
from typing import List

from httpx import AsyncClient
from pydantic import parse_obj_as

from israel_transport_api.config import SIRI_URL, API_KEY
from israel_transport_api.siri.models import MonitoredStopVisit

logging.basicConfig(level=logging.DEBUG)


class SiriClient:
    http_client: AsyncClient

    def __init__(self):
        self.http_client = AsyncClient()

    async def _make_request(self, station_id: int) -> List[MonitoredStopVisit]:
        params = {
            'Key': API_KEY,
            'MonitoringRef': station_id
        }

        resp = await self.http_client.get(SIRI_URL, params=params)
        raw_data: dict = resp.json()
        raw_stop_data: List[dict] = raw_data.get('Siri', {}).get('ServiceDelivery', {}).get('StopMonitoringDelivery', [])

        if len(raw_stop_data) == 0:
            print('no data')
            raise ValueError()

        if raw_stop_data[0]['Status'] != 'true':
            print('error', raw_stop_data)
            raise ValueError()

        parsed_data = parse_obj_as(List[MonitoredStopVisit], raw_stop_data[0]['MonitoredStopVisit'])
        return parsed_data
