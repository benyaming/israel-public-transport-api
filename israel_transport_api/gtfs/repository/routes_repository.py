from typing import Dict, List

from israel_transport_api.gtfs.exceptions import RouteNotFound
from israel_transport_api.gtfs.models import Route

_ROUTES_STORE: Dict[str, Route] = {}


def save_routes(routes: List[Route]):
    for route in routes:
        _ROUTES_STORE[route.id] = route


def save_route(route: Route):
    _ROUTES_STORE[route.id] = route


def find_route_by_id(route_id: str) -> Route:
    try:
        return _ROUTES_STORE[route_id]
    except KeyError:
        raise RouteNotFound(route_id)
