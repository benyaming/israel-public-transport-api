import asyncio
import os
import sys
from contextlib import asynccontextmanager

import uvicorn
import betterlogging as logging
from fastapi import FastAPI
from psycopg.connection_async import AsyncConnection

from israel_transport_api import misc
from israel_transport_api.__version__ import version
from israel_transport_api.config import env
from israel_transport_api.gtfs import init_gtfs_data, stops_router, routes_router
from israel_transport_api.misc import daily_trigger
from israel_transport_api.siri import siri_router


@asynccontextmanager
async def lifespan(_):
    conn = await AsyncConnection.connect(env.DB_DSN)
    app.state.conn = conn

    misc.scheduler.add_job(init_gtfs_data, args=(conn, True,), trigger=daily_trigger)
    misc.scheduler.start()

    asyncio.create_task(init_gtfs_data(conn))

    yield


app = FastAPI(
    root_path=f'/{env.ROOT_PATH}',
    docs_url='/',
    title='Israel public transport API',
    version=version,
    lifespan=lifespan
)


app.include_router(stops_router)
app.include_router(routes_router)
app.include_router(siri_router)

if __name__ == '__main__':
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    uvicorn.run(
        app,
        host='0.0.0.0' if os.getenv('DOCKER_MODE') else '127.0.0.1',
        port=8000,
        use_colors=True,
        log_level=logging.INFO,
        log_config='../uvicorn_logger.json'
    )
