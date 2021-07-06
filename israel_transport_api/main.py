import os

import betterlogging as logging
import uvicorn
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine

from israel_transport_api import misc
from israel_transport_api.__version__ import version
from israel_transport_api.config import ROOT_PATH, DB_URL, DB_NAME
from israel_transport_api.gtfs import init_gtfs_data, init_db, stops_router, routes_router
from israel_transport_api.misc import daily_trigger
from israel_transport_api.siri import siri_router

logging.basic_colorized_config(level=logging.DEBUG)
app = FastAPI(
    root_path=f'/{ROOT_PATH}',
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

    misc.motor_client = AsyncIOMotorClient(DB_URL)
    misc.db_engine = AIOEngine(misc.motor_client, database=DB_NAME)
    misc.db = misc.motor_client[DB_NAME]

    await init_db()
    await init_gtfs_data()


if __name__ == '__main__':
    uvicorn.run(
        app, host='0.0.0.0' if os.getenv('DOCKER_MODE') else '127.0.0.1', port=8000, use_colors=True,
        log_level=logging.DEBUG, log_config='../uvicorn_logger.json'
    )
