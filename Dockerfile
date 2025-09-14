FROM python:3.11 
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv --no-cache-dir && uv sync --group prod --frozen
COPY . .
CMD ["uv", "run", "--no-group", "dev", "gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "app.main:app"]