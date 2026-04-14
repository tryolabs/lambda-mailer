-include .env
export

DEV_OVERRIDES  = Stage=dev FromEmail=hello@tryolabs.com DestinationEmail=german@tryolabs.com FormSharedSecret=$(FORM_SHARED_SECRET)
PROD_OVERRIDES = Stage=prod FromEmail=hello@tryolabs.com DestinationEmail=hello@tryolabs.com FormSharedSecret=$(FORM_SHARED_SECRET)

.PHONY: build deploy-dev deploy-prod logs-dev logs-prod test lint

build:
	sam build --use-container

deploy-dev: build
	sam deploy --config-env dev --parameter-overrides "$(DEV_OVERRIDES)"

deploy-prod: build
	sam deploy --config-env prod --parameter-overrides "$(PROD_OVERRIDES)"

logs-dev:
	sam logs --stack-name lambda-mailer-v2-dev --region us-west-2 --tail

logs-prod:
	sam logs --stack-name lambda-mailer-v2-prod --region us-west-2 --tail

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run ruff format --check .
