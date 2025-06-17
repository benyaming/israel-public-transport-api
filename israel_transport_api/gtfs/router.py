from fastapi import APIRouter, Path, Query, Request

from .models import Stop, Route
from .repository import stops_repository, routes_repository

stops_router = APIRouter(prefix='/stop', tags=['Stop'])
routes_router = APIRouter(prefix='/route', tags=['Route'])


@stops_router.get('/by_code/{stop_code}')
async def find_stop_by_code(
    request: Request,
    stop_code: int = Path(..., description='Stop code', example=5200)
) -> Stop:
    return await stops_repository.find_stop_by_code(stop_code, request.app.state.conn)


@stops_router.get('/by_id/{stop_id}')
async def find_stop_by_id(
    request: Request,
    stop_id: int = Path(..., description='Stop id', example=10846)
) -> Stop:
    return await stops_repository.find_stop_by_id(stop_id, request.app.state.conn)


@stops_router.get('/by_parent_id/{parent_stop_id}')
async def find_stop_by_parent_id(
    request: Request,
    parent_stop_id: int = Path(..., description='Parent stop id', example=48631)
) -> list[Stop]:
    return await stops_repository.find_stops_by_parent_id(parent_stop_id, request.app.state.conn)


@stops_router.get('/near')
async def find_nearest_stops(
    request: Request,
    lat: float = Query(..., description='Latitude', ge=-90, le=90),
    lng: float = Query(..., description='Longitude', ge=-180, le=180),
    radius: int = Query(100, description='Search radius', ge=0, le=5000),
) -> list[Stop]:
    return await stops_repository.find_stops_in_area(lat, lng, radius, request.app.state.conn)


@routes_router.get('/{route_id}')
async def find_route_by_id(request: Request, route_id: int) -> Route:
    return await routes_repository.find_route_by_id(route_id, request.app.state.conn)


@routes_router.get('/available_for_stop/{stop_code}')
async def get_available_routes_for_stop(request: Request, stop_code: int) -> list[Route]:
    return await routes_repository.get_available_routes_for_stop(stop_code, request.app.state.conn)
