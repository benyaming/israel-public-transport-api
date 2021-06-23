import os

import uvicorn
import betterlogging as logging
from fastapi import FastAPI

from bus_api.config import ROOT_PATH
from bus_api.misс import scheduler
from bus_api.gtfs.gtfs_retriever import save_gtfs_data


logging.basic_colorized_config(level=logging.INFO)
app = FastAPI(root_path=ROOT_PATH, docs_url='/', redoc_url='/', title='Bus API')


@app.on_event('startup')
async def on_startup():
    scheduler.start()

    await save_gtfs_data()


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
