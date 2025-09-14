FROM python:3.11 
WORKDIR /app
COPY pyproject.toml .
RUN pip install uv --no-cache-dir && uv sync --group prod
COPY . .
CMD ["uv", "run", "--no-group", "dev", "gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "app.main:app"]