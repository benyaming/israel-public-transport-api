FROM python:3.12-slim

RUN pip install uv
WORKDIR /home/app
COPY . .
WORKDIR /home/app/israel_transport_api
RUN uv sync
ENV TZ=Asia/Jerusalem
ENV PYTHONPATH=/home/app
ENV DOCKER_MODE=true
# Enable MCP Host-header (DNS-rebinding) validation for the deployed host.
ENV MCP_ALLOWED_HOSTS='["api.ginzburg.io", "localhost:*"]'
EXPOSE 8000
CMD ["uv", "run", "python", "main.py"]
