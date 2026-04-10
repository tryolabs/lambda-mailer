# Tryolabs Lambda Mailer

Serverless contact form endpoint deployed to AWS Lambda via [AWS SAM](https://aws.amazon.com/serverless/sam/). Receives a JSON payload and sends an email using Amazon SES.

Built with [FastAPI](https://fastapi.tiangolo.com/) + [Mangum](https://mangum.fastapiexpert.com/) (ASGI→Lambda adapter).

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
- Valid AWS credentials configured (`~/.aws/credentials` or environment variables)
- A verified SES sender email address in your AWS account

## Setup

Install dependencies:

```bash
uv sync --all-extras
```

## Development

Run the API locally (requires SAM CLI):

```bash
sam local start-api --env-vars env.json
```

Or run directly with uvicorn:

```bash
uv run uvicorn api:app --reload
```

### Linting & formatting

```bash
uv run ruff check .
uv run ruff format .
```

### Type checking

```bash
uv run mypy api.py handler.py
```

### Testing

```bash
uv run pytest
```

## Deployment

Deploy to the **dev** environment:

```bash
sam build
sam deploy --config-env dev
```

Deploy to **production**:

```bash
sam build
sam deploy --config-env prod
```

Deploy configuration (stack name, region, email addresses) is defined in `samconfig.toml`.

### Environment variables

Configured as SAM parameters in `samconfig.toml`:

| Variable | Description |
|---|---|
| `FromEmail` | Verified SES sender email address |
| `DestinationEmail` | Email address to receive form submissions |

## Manual testing

With [httpie](https://httpie.org/), invoke the endpoint with the `message.json` test file:

```bash
http POST <endpoint-url> < message.json
```

## License

Copyright (c) 2016 [Tryolabs](https://tryolabs.com).

Released under the MIT License (See LICENSE).
