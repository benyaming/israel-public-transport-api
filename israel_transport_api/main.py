import asyncio
import os

import betterlogging as bl
import uvicorn
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine

from israel_transport_api import misc
from israel_transport_api.__version__ import version
from israel_transport_api.config import env
from israel_transport_api.gtfs import init_gtfs_data, init_db, stops_router, routes_router
from israel_transport_api.misc import daily_trigger
from israel_transport_api.siri import siri_router

app = FastAPI(
    root_path=f'/{env.ROOT_PATH}',
    docs_url='/',
    redoc_url='/re_doc',
    title='Israel public transport API',
    version=version
)

app.include_router(stops_router)
app.include_router(routes_router)
app.include_router(siri_router)


@app.on_event('startup')
async def on_startup():
    misc.scheduler.add_job(init_gtfs_data, args=(True,), trigger=daily_trigger)
    misc.scheduler.start()

    misc.motor_client = AsyncIOMotorClient(env.DB_URL)
    misc.db_engine = AIOEngine(misc.motor_client, database=env.DB_NAME)
    misc.db = misc.motor_client[env.DB_NAME]

    await init_db()
    asyncio.create_task(init_gtfs_data())


if __name__ == '__main__':
    uvicorn.run(
        app,
        host='0.0.0.0' if os.getenv('DOCKER_MODE') else '127.0.0.1',
        port=8000,
        use_colors=True,
        log_level=bl.DEBUG,
        log_config='../uvicorn_logger.json'
    )
