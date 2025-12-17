FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install project
COPY pyproject.toml README.md MANIFEST.in ./
COPY src ./src

RUN python -m pip install --no-cache-dir -U pip \
  && python -m pip install --no-cache-dir .

EXPOSE 8000

# ModelScope-style: use $PORT if provided
CMD ["sh", "-c", "dependence-analysis-mcp --host 0.0.0.0 --port ${PORT:-8000} --log-level ${LOG_LEVEL:-info}"]
