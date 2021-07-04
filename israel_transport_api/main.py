import asyncio
import os

import uvicorn
import betterlogging as logging
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine

from israel_transport_api.config import ROOT_PATH, DB_URL, DB_NAME
from israel_transport_api import misc
from israel_transport_api.gtfs import init_gtfs_data, init_db
from israel_transport_api.misc import daily_trigger

logging.basic_colorized_config(level=logging.DEBUG)
app = FastAPI(root_path=ROOT_PATH, docs_url='/', redoc_url='/', title='Israel public transport API')


@app.on_event('startup')
async def on_startup():
    misc.scheduler.add_job(init_gtfs_data, args=(True,), trigger=daily_trigger)
    misc.scheduler.start()

    misc.motor_client = AsyncIOMotorClient(DB_URL)
    misc.db_engine = AIOEngine(misc.motor_client, database=DB_NAME)
    misc.db = misc.motor_client[DB_NAME]

    await init_db()
    await init_gtfs_data()


@app.on_event('shutdown')
async def on_shutdown():
    ...


@app.get('get_lines/{stop_number}')
async def get_lines(stop_number: int) -> dict:
    ...


if __name__ == '__main__':
    uvicorn.run(
        app,
        host='0.0.0.0' if os.getenv('DOCKER_MODE') else '127.0.0.1',
        port=8000,
        use_colors=True,
        log_level=logging.DEBUG,
        log_config='../uvicorn_logger.json'
    )
