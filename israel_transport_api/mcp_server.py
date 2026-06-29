"""MCP interface for the Israel public transport API.

Exposes the same stops / routes / real-time-arrivals operations as MCP tools over
streamable HTTP. The server is mounted onto the FastAPI app (see ``main.py``) and
shares its database connection, which is injected via :func:`set_connection` during
the app lifespan.
"""
import logging

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from psycopg.connection_async import AsyncConnection

from israel_transport_api.config import env
from israel_transport_api.gtfs.models import Stop, Route
from israel_transport_api.gtfs.repository import stops_repository, routes_repository
from israel_transport_api.siri.client import get_incoming_routes, get_vehicle_location as _get_vehicle_location
from israel_transport_api.siri.models import IncomingRoutesResponse
from israel_transport_api.siri.siri_models import VehicleLocation

logger = logging.getLogger('mcp_server')

# The streamable endpoint lives at "/mcp"; the app is mounted at the root (see
# main.py). Mounting the sub-app at "/mcp" instead would leave its route at "/",
# which makes Starlette 307-redirect "/mcp" -> "/mcp/" — and behind a path-stripping
# reverse proxy that redirect drops the prefix and the client never connects.
mcp = FastMCP(
    'Israel public transport',
    stateless_http=True,
    streamable_http_path='/mcp',
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=bool(env.MCP_ALLOWED_HOSTS),
        allowed_hosts=env.MCP_ALLOWED_HOSTS,
        allowed_origins=env.MCP_ALLOWED_ORIGINS,
    ),
)

# Database connection shared with the FastAPI app; set during the app lifespan.
_conn: AsyncConnection | None = None


def set_connection(conn: AsyncConnection) -> None:
    global _conn
    _conn = conn


def _get_conn() -> AsyncConnection:
    if _conn is None:
        raise RuntimeError('Database connection is not initialized')
    return _conn


# Upper bound on result size for caller-controlled (LLM) `limit` arguments.
_MAX_LIMIT = 100


def _clamp_limit(limit: int) -> int:
    return max(1, min(limit, _MAX_LIMIT))


@mcp.tool()
async def find_stop_by_code(stop_code: int) -> Stop:
    """Find a public transport stop by its public stop code (e.g. 5200)."""
    return await stops_repository.find_stop_by_code(stop_code, _get_conn())


@mcp.tool()
async def find_stop_by_id(stop_id: int) -> Stop:
    """Find a public transport stop by its internal GTFS stop id (e.g. 10846)."""
    return await stops_repository.find_stop_by_id(stop_id, _get_conn())


@mcp.tool()
async def search_stops_by_name(query: str, limit: int = 20) -> list[Stop]:
    """Search for stops by (partial) name, e.g. "בנייני האומה" or "Savidor".
    Use this to turn a place the user named into concrete stops before fetching
    arrivals or routes. Returns up to `limit` matches (capped at 100), prefix matches first."""
    return await stops_repository.search_stops_by_name(query, _get_conn(), _clamp_limit(limit))


@mcp.tool()
async def find_stops_by_parent_id(parent_stop_id: int) -> list[Stop]:
    """List the child stops / platforms belonging to a parent station id (e.g. 48631)."""
    return await stops_repository.find_stops_by_parent_id(parent_stop_id, _get_conn())


@mcp.tool()
async def find_nearest_stops(lat: float, lng: float, radius: int = 100) -> list[Stop]:
    """Find stops within ``radius`` meters of a latitude/longitude point (radius max 5000)."""
    radius = max(0, min(radius, 5000))
    return await stops_repository.find_stops_in_area(lat, lng, radius, _get_conn())


@mcp.tool()
async def find_route_by_id(route_id: int) -> Route:
    """Get a route by its GTFS route id."""
    return await routes_repository.find_route_by_id(route_id, _get_conn())


@mcp.tool()
async def search_routes(query: str, limit: int = 20) -> list[Route]:
    """Search for routes/lines by line number (short name) or origin/destination city,
    e.g. "480" or "חיפה". Returns up to `limit` de-duplicated matches (capped at 100),
    exact line-number matches first."""
    return await routes_repository.search_routes(query, _get_conn(), _clamp_limit(limit))


@mcp.tool()
async def get_available_routes_for_stop(stop_code: int) -> list[Route]:
    """List all routes that serve a given stop code."""
    return await routes_repository.get_available_routes_for_stop(stop_code, _get_conn())


@mcp.tool()
async def get_arrivals_for_stop(stop_code: int, monitoring_interval: int = 30) -> IncomingRoutesResponse:
    """Get real-time (SIRI) incoming routes and ETAs for a stop code within the next
    ``monitoring_interval`` minutes."""
    return await get_incoming_routes(_get_conn(), stop_code=stop_code, monitoring_interval=monitoring_interval)


@mcp.tool()
async def get_arrivals_for_stop_by_id(stop_id: int, monitoring_interval: int = 30) -> IncomingRoutesResponse:
    """Get real-time (SIRI) incoming routes and ETAs for a stop, addressed by its GTFS
    stop id, within the next ``monitoring_interval`` minutes."""
    return await get_incoming_routes(_get_conn(), stop_id=stop_id, monitoring_interval=monitoring_interval)


@mcp.tool()
async def get_vehicle_location(vehicle_plate_number: str, stop_code: int) -> VehicleLocation:
    """Get the current GPS location (lat/lng) of a specific vehicle, identified by its
    license-plate / vehicle ref, that is currently inbound to the given stop code.
    Answers "where is my bus right now?". The vehicle ref comes from the `plate_number`
    field of `get_arrivals_for_stop`. Errors if the vehicle is not currently reported as
    approaching that stop."""
    return await _get_vehicle_location(vehicle_plate_number, stop_code)
