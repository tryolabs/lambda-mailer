import os
import re

import boto3
from botocore.exceptions import ClientError
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator

FROM_EMAIL = os.environ["FROM_EMAIL"]
DESTINATION_EMAIL = os.environ["DESTINATION_EMAIL"]
FORM_SHARED_SECRET = os.environ.get("FORM_SHARED_SECRET")

app = FastAPI(title="Lambda Mailer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["OPTIONS", "POST"],
    allow_headers=["Content-Type", "Authorization", "X-Form-Secret"],
)

AWS_REGION = os.environ.get("AWS_DEFAULT_REGION", os.environ.get("AWS_REGION", "us-east-1"))

ses = boto3.client("ses", region_name=AWS_REGION)

EMAIL_REGEXP = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


async def verify_secret(x_form_secret: str | None = Header(default=None)) -> None:
    """Reject requests that don't carry the correct shared secret header.

    Bots POST directly to the Lambda URL and bypass all frontend validation.
    Only the Next.js backend knows the secret, so direct bot traffic gets a 403.
    Fails closed: if FORM_SHARED_SECRET is not configured, all requests are denied.
    """
    if not FORM_SHARED_SECRET or x_form_secret != FORM_SHARED_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")


class ContactForm(BaseModel):
    name: str
    email: str
    message: str

    # Allow extra fields (e.g. "budget", "_important")
    model_config = {"extra": "allow"}

    @field_validator("name", "email", "message")
    @classmethod
    def must_not_be_blank(cls, v: str, info: object) -> str:
        if not v.strip():
            raise ValueError(f'The "{info.field_name}" field cannot be empty or spaces.')  # type: ignore[union-attr]
        return v

    @field_validator("email")
    @classmethod
    def must_be_valid_email(cls, v: str) -> str:
        if not EMAIL_REGEXP.match(v):
            raise ValueError('The "email" field needs to be a valid email address.')
        return v


@app.exception_handler(ClientError)
async def ses_error_handler(request: Request, exc: ClientError) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"status": "error", "error": str(exc)},
    )


@app.post("/", dependencies=[Depends(verify_secret)])
async def send_email(form: ContactForm) -> JSONResponse:
    extra_fields = set(form.model_dump().keys()) - {"name", "email", "message"}

    # Honeypot: if "_important" is present, a bot likely submitted the form
    if "_important" in extra_fields:
        return JSONResponse(content={"status": "ok"}, status_code=200)

    other_fields_html = "\n".join(
        f"<strong>{field}</strong>: {form.model_dump()[field]}<br>"
        for field in sorted(extra_fields)
    )

    subject = f"Tryolabs contact form message from {form.name} ({form.email})"
    message_html = f"""<strong>name</strong>: {form.name}<br>
<strong>email</strong>: {form.email}<br>
{other_fields_html}
<p>
{form.message.replace(chr(10), "<br>")}
</p>
"""

    response = ses.send_email(
        Source=FROM_EMAIL,
        Destination={"ToAddresses": [DESTINATION_EMAIL]},
        Message={
            "Subject": {"Data": subject, "Charset": "utf-8"},
            "Body": {"Html": {"Data": message_html, "Charset": "utf-8"}},
        },
        ReplyToAddresses=[form.email],
        ReturnPath=FROM_EMAIL,
    )

    if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
        status_code = response["ResponseMetadata"]["HTTPStatusCode"]
        return JSONResponse(
            content={"status": "error", "error": f"SES responded with {status_code}"},
            status_code=500,
        )

    return JSONResponse(content={"status": "ok"}, status_code=200)
