import logging

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
        route = await (
            await conn.cursor().execute(
                'SELECT * FROM routes WHERE id = %s',
                (route_id,)
            )
        ).fetchone()

        if not route:
            raise RouteNotFound(route_id)
        route = Route.from_row(route)
        _ROUTES_CACHE[route_id] = route

    return route


async def get_all_routes(conn: AsyncConnection) -> list[Route]:
    routes = await (await conn.cursor().execute('SELECT * FROM routes')).fetchall()
    return [Route.from_row(route) for route in routes]


async def get_routes_for_stop(stop_code: int, conn: AsyncConnection) -> list[Route]:
    query = '''
        SELECT DISTINCT r.*
        FROM routes r
            JOIN trips t ON r.id = t.route_id
            JOIN stop_times st ON t.id = st.trip_id
            JOIN stops s ON st.stop_id = s.id
        WHERE s.code = %s
    '''
    routes = await (await conn.cursor().execute(query, (stop_code,))).fetchall()
    return [Route.from_row(route) for route in routes]
