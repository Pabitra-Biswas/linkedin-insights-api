LinkedIn Insights — Quick start
--------------------------------

Prerequisites:
- Docker / Docker Compose
- Python 3.11+ and virtualenv (for running tests locally)

1) Copy env example

Create a `.env` at the repo root from the example:

```
cp .env.example .env
```

Edit values as needed. Minimum useful envs:
- `MONGODB_URL` (e.g. `mongodb://mongo:27017` when using docker-compose)
- `MONGODB_DB_NAME` (defaults to `linkedin_insights`)
- `REDIS_URL` (defaults to `redis://localhost:6379`)
- `LOCAL_STORAGE_PATH` (where images/uploads will be stored)
- `GEMINI_API_KEY` (optional — used for AI summaries)

2) Start local services

From the `linkedin-insights` folder run:

```
docker-compose up -d
```

This starts `mongo` and `redis` used by the API. Wait a few seconds for services to be healthy.

3) Run the API

```
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4) Open the API docs

Point a browser to: `http://localhost:8000/docs` to try endpoints interactively (or `http://localhost:8000/openapi.json`).

5) Example requests

- Get page details (will try cache → DB → scrape if not found):

```
curl 'http://localhost:8000/api/v1/pages/microsoft?force_refresh=false'
```

- Get page posts:

```
curl 'http://localhost:8000/api/v1/pages/microsoft/posts?page=1&page_size=10'
```

- Get AI summary for a page (page must exist in DB):

```
curl 'http://localhost:8000/api/v1/pages/microsoft/ai-summary'
```

6) Run tests locally

```
pip install -r requirements.txt
pytest -q
```

Notes:
- Scraping LinkedIn requires Chrome and the `undetected-chromedriver` environment. For CI or quick tests, prefer running with a pre-seeded page in the DB or mock/stub the `LinkedInScraper`.
- For security: remove any hard-coded credentials (the file `tests/test_mongo.py` in this repo contains a literal Mongo URI — replace it with an env-var based test or remove it).

If you'd like, I can add a `.env.example`, sanitize `tests/test_mongo.py`, and add a short end-to-end test script.
