import os

import uvicorn
import betterlogging as logging
from fastapi import FastAPI
from aiopg import create_pool

from israel_transport_api.config import ROOT_PATH, DB_DSN
from israel_transport_api import misс
from israel_transport_api.gtfs import init_gtfs_data


logging.basic_colorized_config(level=logging.INFO)
app = FastAPI(root_path=ROOT_PATH, docs_url='/', redoc_url='/', title='Israel public transport API')


@app.on_event('startup')
async def on_startup():
    misс.scheduler.start()
    misс.pool = create_pool(DB_DSN)

    await init_gtfs_data()


@app.on_event('shutdown')
async def on_shutdown():
    misс.pool.close()


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
