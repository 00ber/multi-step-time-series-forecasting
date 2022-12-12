.PHONY: build-backend
build-backend: ## Build backend services
	docker build -f Dockerfile.backend -t pred-backend ./backend

.PHONY: build-frontend
build-frontend: ## Build frontend services
	docker build -f Dockerfile.frontend -t pred-frontend ./frontend

.PHONY: up-prod
up-prod: ## Build backend services
	docker build -f Dockerfile.backend -t pred-backend ./backend
	docker build -f Dockerfile.frontend -t pred-frontend ./frontend
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d 

.PHONY: up-dev
up-dev: ## Build backend services
	docker build -f Dockerfile.backend -t pred-backend ./backend
	docker build -f Dockerfile.frontend -t pred-frontend ./frontend
	docker-compose up -d 
