# Tryolabs Lambda Mailer

Serverless contact form endpoint deployed to AWS Lambda via [AWS SAM](https://aws.amazon.com/serverless/sam/). Receives a JSON payload and sends an email using Amazon SES.

Built with [FastAPI](https://fastapi.tiangolo.com/) + [Mangum](https://mangum.fastapiexpert.com/) (ASGI→Lambda adapter).

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
- [Docker](https://www.docker.com/) (required for `sam build --use-container`)
- Valid AWS credentials configured (`~/.aws/credentials` or environment variables)
- A verified SES sender email address in your AWS account

## Setup

**1. Install dependencies:**

```bash
uv sync --all-extras
```

**2. Configure secrets:**

```bash
cp .env.example .env
# Edit .env and fill in FORM_SHARED_SECRET with a strong random value:
openssl rand -hex 32
```

`.env` is gitignored — never commit it.

## Deployment

All deploy commands are in the `Makefile` and read secrets from `.env` automatically.

Deploy to **dev**:

```bash
make deploy-dev
```

Deploy to **production**:

```bash
make deploy-prod
```

### Environment variables / parameters

| Parameter | Source | Description |
|---|---|---|
| `FromEmail` | `samconfig.toml` | Verified SES sender address |
| `DestinationEmail` | `samconfig.toml` | Address to receive form submissions |
| `FormSharedSecret` | `.env` | Shared secret — Next.js sends this in `X-Form-Secret` header; requests without it are rejected with 403 |

Other deploy config (stack name, region) is in `samconfig.toml`.

## Development

Run the API locally (requires SAM CLI):

```bash
sam local start-api --env-vars env.json
```

Or directly with uvicorn:

```bash
uv run uvicorn api:app --reload
```

### Linting & formatting

```bash
make lint
# or individually:
uv run ruff check .
uv run ruff format .
```

### Type checking

```bash
uv run mypy api.py handler.py
```

### Testing

```bash
make test
# or:
uv run pytest
```

### Logs

```bash
make logs-dev   # tail dev Lambda logs
make logs-prod  # tail prod Lambda logs
```

## Manual testing

With [httpie](https://httpie.org/), invoke the endpoint with the `message.json` test file:

```bash
http POST <endpoint-url> X-Form-Secret:<secret> < message.json
```

## License

Copyright (c) 2016 [Tryolabs](https://tryolabs.com).

Released under the MIT License (See LICENSE).

