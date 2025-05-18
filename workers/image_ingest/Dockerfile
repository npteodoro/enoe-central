FROM python:alpine

WORKDIR /app

COPY workers/image_ingest/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY workers /app/workers

ENV PYTHONPATH="/app/workers:${PYTHONPATH}"

CMD ["celery", "-A", "image_ingest.main", "worker", "--loglevel=info"]