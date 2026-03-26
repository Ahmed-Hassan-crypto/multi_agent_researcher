.PHONY: help install test lint docker-build docker-run deploy-ec2 clean

help:
	@echo "Available commands:"
	@echo "  make install        - Install dependencies"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Run linting"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-run    - Run Docker container"
	@echo "  make deploy-ec2    - Deploy to EC2"

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v --cov=agent --cov=utils

lint:
	ruff check .
	ruff format --check .

docker-build:
	docker build -t multi-agent-researcher .

docker-run:
	docker run -p 8501:8501 -p 8000:8000 --env-file .env multi-agent-researcher

docker-compose:
	docker-compose up --build

deploy-ec2:
	@echo "Deploying to EC2..."
	@echo "1. Launch EC2 instance"
	@echo "2. SSH into instance"
	@echo "3. Run: git clone <your-repo> && cd multi_agent_researcher"
	@echo "4. Run: make install"
	@echo "5. Run: make docker-run"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pdf" -delete
	rm -rf .pytest_cache .coverage htmlcov
