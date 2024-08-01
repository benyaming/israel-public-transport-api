FROM python:3.9-slim

RUN pip install pdm
WORKDIR /home/app
COPY . .
WORKDIR /home/app/israel_transport_api
RUN pipenv install
ENV TZ=Asia/Jerusalem
ENV PYTHONPATH=/home/app
ENV DOCKER_MODE=true
EXPOSE 8000
CMD ["pdm", "run", "python", "main.py"]
