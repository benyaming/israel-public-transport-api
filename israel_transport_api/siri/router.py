from asyncio import sleep

from fastapi import APIRouter, Path, Query, Request, WebSocket, WebSocketDisconnect

from israel_transport_api.siri.client import get_incoming_routes, get_vehicle_location
from israel_transport_api.siri.models import IncomingRoutesResponse
from israel_transport_api.config import env


siri_router = APIRouter(prefix='/siri', tags=['Siri'])


@siri_router.get('/get_routes_for_stop/{stop_code}')
async def get_routes_for_stop(
        request: Request,
        stop_code: int = Path(..., description='Stop code', example=5200),
        monitoring_interval: int = Query(30, description='Monitoring interval in minutes')
) -> IncomingRoutesResponse:
    return await get_incoming_routes(request.app.state.conn, stop_code, monitoring_interval)


@siri_router.websocket('/track_vehicle/{stop_code}/{vehicle_plate_number}')
async def track_vehicle(
        ws: WebSocket,
        stop_code: int = Path(..., description='Stop code for tracking'),
        vehicle_plate_number: str = Path(..., description='Vehicle plate number')
):
    await ws.accept()
    try:
        previous_resp = None
        while True:
            resp = await get_vehicle_location(vehicle_plate_number, stop_code)
            resp and previous_resp != resp and await ws.send_json(resp.model_dump())
            previous_resp = resp
            await sleep(env.WS_UPDATE_INTERVAL)
    except WebSocketDisconnect:
        pass
