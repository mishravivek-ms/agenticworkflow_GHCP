.PHONY: backend frontend test install

backend:
	cd backend && uvicorn main:app --reload --port 8000

frontend:
	cd frontend && uvicorn main:app --reload --port 3000

test:
	cd backend && python -m pytest tests/ -v

install:
	cd backend && uv pip install -e .
	cd frontend && uv pip install -e .
