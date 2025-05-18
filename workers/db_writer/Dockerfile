FROM python:alpine

WORKDIR /app

COPY workers/db_writer/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY workers /app/workers

ENV PYTHONPATH="/app/workers:${PYTHONPATH}"

CMD ["celery", "-A", "db_writer.main", "worker", "--loglevel=info"]