import logging

from anymail.signals import tracking
from django.conf import settings
from django.core.mail import EmailMessage
from django.dispatch import receiver

from sandwich.core.models import Organization
from sandwich.core.service.template_service import render
from sandwich.core.types import HtmlStr

logger = logging.getLogger(__name__)


def send_templated_email(  # noqa: PLR0913
    to: str,
    subject_template: str,
    body_template: str,
    context: dict[str, object],
    organization: Organization | None = None,
    language: str | None = None,
):
    context.setdefault("app_url", settings.APP_URL)
    subject = render(
        template_name=subject_template,
        organization=organization,
        language=language,
        context=context,
        as_markdown=False,
    )
    body = render(template_name=body_template, organization=organization, language=language, context=context)
    send_email(to, subject, body)


def send_email(to: str, subject: str, body: HtmlStr):
    logger.info(
        "Sending email",
        extra={
            "has_recipient": bool(to),
            "subject_length": len(subject) if subject else 0,
            "body_length": len(body) if body else 0,
        },
    )

    # TODO: set up bounce tracking, etc.
    # see https://anymail.dev/en/stable/esps/amazon_ses/#status-tracking-webhooks
    if not to:
        # TODO: should this throw instead?
        logger.warning("Dropping email - no recipient specified", extra={"subject": subject})
        return

    msg = EmailMessage(
        subject=subject,
        body=body,
        from_email=None,
        to=[to],
    )
    msg.content_subtype = "html"

    try:
        msg.send()
        logger.info("Email sent successfully", extra={"has_recipient": bool(to)})
    except Exception as e:
        logger.exception("Failed to send email", extra={"error_type": type(e).__name__})


@receiver(tracking)
def handle_tracking(sender, event, esp_name, **kwargs):
    if esp_name == "Amazon SES":
        logger.info("Received email tracking event")
        if event.event_type == "bounced":
            logger.warning("Email bounced", extra={"reason": event.reject_reason, "message_id": event.message_id})
            # TODO: Update email record in db
