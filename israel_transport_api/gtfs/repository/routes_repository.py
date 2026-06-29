import logging
import re

from psycopg.connection_async import AsyncConnection

from israel_transport_api.gtfs.exceptions import RouteNotFound
from israel_transport_api.gtfs.models import Route

_ROUTES_CACHE: dict[int, Route] = {}


logger = logging.getLogger(__name__)


async def invalidate_route_cache(conn: AsyncConnection):
    logger.info('Invalidating route cache...')

    routes = await get_all_routes(conn)
    _ROUTES_CACHE.clear()
    for route in routes:
        _ROUTES_CACHE[route.id] = route

    logger.info('Route cache invalidated.')


async def find_route_by_id(route_id: int, conn: AsyncConnection) -> Route:
    try:
        return _ROUTES_CACHE[route_id]
    except KeyError:
        query = '''
            SELECT * FROM routes r
            LEFT JOIN agencies a ON a.id = r.agency_id
            WHERE r.id = %s
        '''
        route = await (
            await conn.cursor().execute(
                query,
                (route_id,)
            )
        ).fetchone()

        if not route:
            raise RouteNotFound(route_id)

        route = Route.from_row(route)
        _ROUTES_CACHE[route_id] = route

    return route


async def get_all_routes(conn: AsyncConnection) -> list[Route]:
    query = '''
         SELECT * FROM routes r
         LEFT JOIN agencies a ON a.id = r.agency_id
     '''
    routes = await (await conn.cursor().execute(query)).fetchall()
    return [Route.from_row(route) for route in routes]


def _route_sort_key(route: Route, query: str | None = None):
    digits = re.sub(r'\D', '', route.short_name)
    numeric = int(digits) if digits else 0
    # Exact short_name matches first (when searching), then by numeric line, then name.
    return route.short_name != query, numeric, route.short_name


async def search_routes(query: str, conn: AsyncConnection, limit: int = 20) -> list[Route]:
    pattern = f'%{query}%'
    resp = await (await conn.cursor().execute(
        '''
            SELECT DISTINCT r.*, a.*
            FROM routes r
            LEFT JOIN agencies a ON a.id = r.agency_id
            WHERE r.short_name ILIKE %s
               OR r.from_city ILIKE %s
               OR r.to_city ILIKE %s
               OR r.description ILIKE %s
        ''',
        (pattern, pattern, pattern, pattern)
    )).fetchall()
    routes = [Route.from_row(route) for route in resp]

    # Collapse trip/direction variants that share the same line, agency and endpoints.
    routes = list({
        (route.short_name, route.agency.id, route.from_city, route.to_city): route
        for route in routes
    }.values())

    routes.sort(key=lambda r: _route_sort_key(r, query))
    return routes[:limit]


async def get_available_routes_for_stop(stop_code: int, conn: AsyncConnection) -> list[Route]:
    query = '''
        SELECT DISTINCT r.*, a.*
        FROM routes_for_stop rfs
        LEFT JOIN routes r ON r.id = ANY(rfs.route_ids)
        LEFT JOIN agencies a ON a.id = r.agency_id
        WHERE rfs.stop_code = %s;
    '''
    resp = await (await conn.cursor().execute(query, (stop_code,))).fetchall()
    routes = [Route.from_row(route) for route in resp]

    # Remove routes with the same short_name and agency
    routes = list({(route.short_name, route.agency.id): route for route in routes}.values())

    routes.sort(key=lambda r: int(re.sub(r'\D', '', r.short_name)) or 0)
    return routes
