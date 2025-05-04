---

**`README.md`**

````markdown
# ENOE‑Central

**ENOE‑Central** is the orchestration backend for the ENOE distributed flood‑forecast system. It ingests sensor reports and alerts from edge gateways, persists time‑series data, exposes REST APIs, and coordinates model updates to the field.

## Features

- MQTT subscription (Mosquitto) for `enoe/report`, `enoe/alert`, `enoe/control`  
- Factory → Job → Worker pattern (Celery/RQ) for asynchronous processing  
- Time‑series storage (InfluxDB / TimescaleDB / PostgreSQL+Timescale)  
- Prometheus metrics for Grafana monitoring  
- FastAPI REST endpoints for data querying and control commands  
- Health‑check endpoints for container orchestration  
- Configurable via YAML and environment variables  
- Dockerized for local development and production  

## Quickstart

1. **Clone repository**  
   ```bash
   git clone https://your‑repo-url.git enoe-central
   cd enoe-central
````

2. **Configure environment**
   Copy and edit your environment files:

   ```bash
   cp config/env/.env.example config/env/.env
   # then fill in MQTT, TSDB, JWT, Celery broker settings
   ```

3. **Build & run with Docker Compose**

   ```bash
   docker-compose up --build
   ```

   * FastAPI will be available at `http://localhost:8000`
   * Prometheus metrics at `http://localhost:8000/metrics`
   * Celery workers will auto‑connect to Redis and process jobs

4. **Run tests**

   ```bash
   pytest tests/unit
   pytest tests/integration
   ```

## Project Structure

```
enoe-central/
├── api/               # FastAPI routes & middleware
├── config/            # YAML config and .env examples
├── jobs/              # Job definitions & factory
├── models/            # ML model metadata & registry
├── services/          # MQTT, TSDB, notifier, auth, monitoring
├── storage/           # Cache and TSDB adapters
├── workers/           # Celery/RQ worker entrypoints
├── domain/            # Business‑logic entities & services
├── tests/             # Unit & integration tests
├── scripts/           # Helper scripts (setup, deploy, backup)
├── migrations/        # Alembic database migrations
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Configuration

All runtime settings live in `config/*.yaml` and environment variables under `config/env/*.yaml` (or `.env`). Key files:

* `config/app.yaml` – application settings
* `config/mqtt.yaml` – MQTT broker connection
* `config/tsdb.yaml` – time‑series database
* `config/celery.yaml` – Celery broker & worker
* `config/logging.yaml` – logging configuration

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on code style, testing, and PR process.

---

````

