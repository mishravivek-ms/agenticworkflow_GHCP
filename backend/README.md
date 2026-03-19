# Backend — FastAPI

REST API backend built with **FastAPI** and managed via **uv**.

## Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) installed

## Setup

```bash
# From the backend/ directory
uv sync
```

## Running the server

```bash
uv run uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.

Interactive docs: `http://localhost:8000/docs`

## Project structure

```
backend/
├── app/
│   ├── main.py          # FastAPI application entry point
│   ├── core/
│   │   └── config.py    # Application settings (pydantic-settings)
│   ├── models/
│   │   └── item.py      # Pydantic request/response models
│   ├── routers/
│   │   └── items.py     # /api/v1/items CRUD router
│   └── services/
│       └── item_service.py  # Business logic / data layer
└── pyproject.toml
```

## Example API usage

```bash
# Create an item
curl -X POST http://localhost:8000/api/v1/items/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Widget", "price": 9.99}'

# List all items
curl http://localhost:8000/api/v1/items/

# Get a single item
curl http://localhost:8000/api/v1/items/1

# Update an item
curl -X PUT http://localhost:8000/api/v1/items/1 \
  -H "Content-Type: application/json" \
  -d '{"price": 4.99}'

# Delete an item
curl -X DELETE http://localhost:8000/api/v1/items/1
```
