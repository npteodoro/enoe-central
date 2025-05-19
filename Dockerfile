FROM python:alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src .

RUN adduser -D -g '' appuser && \
    find . -type d -exec chmod 755 {} \; && \
    find . -type f -exec chmod 644 {} \;

USER appuser

CMD ["python", "-u", "main.py"]
