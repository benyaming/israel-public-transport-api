from israel_transport_api.main import app
import uvicorn
import os
import logging

if __name__ == '__main__':
    uvicorn.run(
        app,
        host='0.0.0.0' if os.getenv('DOCKER_MODE') else '127.0.0.1',
        port=8000,
        use_colors=True,
        log_level=logging.DEBUG,
        log_config='uvicorn_logger.json'
    )
