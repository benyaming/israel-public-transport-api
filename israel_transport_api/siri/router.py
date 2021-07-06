from fastapi import APIRouter, Path, Query

from israel_transport_api.siri.client import get_incoming_routes
from israel_transport_api.siri.models import IncomingRoutesResponse

siri_router = APIRouter(prefix='/siri', tags=['Siri'])


@siri_router.get('/get_routes_for_stop/{stop_code}', response_model=IncomingRoutesResponse)
async def get_routes_for_stop(
        stop_code: int = Path(..., description='Stop code', example=5200),
        monitoring_interval: int = Query(30, description='Monitoring interval in minutes')
) -> IncomingRoutesResponse:
    return await get_incoming_routes(stop_code, monitoring_interval)
