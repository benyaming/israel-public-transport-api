import os

import uvicorn
import betterlogging as logging
from fastapi import FastAPI

from bus_api.config import ROOT_PATH

logging.basic_colorized_config(level=logging.INFO)
app = FastAPI(root_path=ROOT_PATH, docs_url='/', redoc_url='/', title='Bus API')


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
