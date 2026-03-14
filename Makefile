.PHONY: dev migrate test lint worker logs clean model-pull spacy-pull test-integration test-all prod-up coverage

dev:
	docker compose up -d --build
	@echo "Waiting for services to start..."
	ping 127.0.0.1 -n 6 > nul
	$(MAKE) migrate

dev-local:
	@echo "Starting backend..."
	start powershell -Command "cd backend; .\venv\Scripts\python.exe -m uvicorn app.main:app --port 8000 --host 0.0.0.0 --reload"
	@echo "Starting frontend..."
	start powershell -Command "cd frontend; npm run dev -- --port 3000"

local-setup:
	@echo "Setting up local environment..."
	cd backend && py -3.12 -m venv venv
	cd backend && .\venv\Scripts\python.exe -m pip install -r requirements.txt
	cd backend && .\venv\Scripts\python.exe -m pip install python-magic-bin
	cd backend && .\venv\Scripts\python.exe -m spacy download en_core_web_sm
	cd frontend && npm install

migrate:
	docker compose exec -T backend alembic upgrade head

test:
	docker compose exec -T backend pytest app/ -v

test-integration:
	docker compose exec -T backend pytest tests/integration/ -v

test-all:
	$(MAKE) test
	$(MAKE) test-integration

lint:
	docker compose exec -T backend ruff check .

worker:
	docker compose exec -T backend celery -A app.celery worker --loglevel=debug

logs:
	docker compose logs -f backend worker

clean:
	docker compose down -v --remove-orphans

model-pull:
	docker compose exec -T backend python /app/scripts/download_bert_model.py

spacy-pull:
	docker compose exec -T backend python -m spacy download en_core_web_sm

prod-up:
	docker compose -f docker-compose.prod.yml up -d

coverage:
	docker compose exec -T backend pytest --cov=app --cov-report=html
