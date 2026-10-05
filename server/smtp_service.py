import os
import smtplib

from email.message import EmailMessage


# ============================================================
# SMTP Configuration
# ============================================================

SMTP_HOST = os.getenv(
    "SMTP_HOST",
    ""
)

SMTP_PORT = int(
    os.getenv(
        "SMTP_PORT",
        "587"
    )
)

SMTP_USERNAME = os.getenv(
    "SMTP_USERNAME",
    ""
)

SMTP_PASSWORD = os.getenv(
    "SMTP_PASSWORD",
    ""
)

SMTP_FROM = os.getenv(
    "SMTP_FROM",
    ""
)

SMTP_USE_TLS = os.getenv(
    "SMTP_USE_TLS",
    "true"
).lower() == "true"


# ============================================================
# Check SMTP Configuration
# ============================================================

def smtp_configured():

    return bool(
        SMTP_HOST
        and SMTP_USERNAME
        and SMTP_PASSWORD
        and SMTP_FROM
    )


# ============================================================
# Send Email
# ============================================================

def send_email(
    recipient,
    subject,
    body
):

    if not smtp_configured():

        print(
            "[SMTP] SMTP is not configured. "
            "Email notification skipped."
        )

        return {
            "success": False,
            "configured": False,
            "message": "SMTP is not configured."
        }

    message = EmailMessage()

    message["From"] = SMTP_FROM

    message["To"] = recipient

    message["Subject"] = subject

    message.set_content(
        body
    )

    try:

        if SMTP_USE_TLS:

            with smtplib.SMTP(
                SMTP_HOST,
                SMTP_PORT,
                timeout=15
            ) as smtp:

                smtp.ehlo()

                smtp.starttls()

                smtp.ehlo()

                smtp.login(
                    SMTP_USERNAME,
                    SMTP_PASSWORD
                )

                smtp.send_message(
                    message
                )

        else:

            with smtplib.SMTP(
                SMTP_HOST,
                SMTP_PORT,
                timeout=15
            ) as smtp:

                smtp.ehlo()

                smtp.login(
                    SMTP_USERNAME,
                    SMTP_PASSWORD
                )

                smtp.send_message(
                    message
                )

        print(
            f"[SMTP] Email sent to {recipient}"
        )

        return {
            "success": True,
            "message": "Email sent successfully."
        }

    except Exception as error:

        print(
            f"[SMTP] Email sending failed: {error}"
        )

        return {
            "success": False,
            "configured": True,
            "message": f"SMTP error: {error}"
        }


# ============================================================
# Request Notification
# ============================================================

def send_request_notification(
    recipient,
    student_name,
    request_id,
    subject,
    status,
    message
):

    email_subject = (
        f"Campus Help Request #{request_id} "
        f"Update"
    )

    email_body = f"""
Hello {student_name},

There has been an update to your Campus Help request.

Request ID: #{request_id}
Subject: {subject}
Current Status: {status}

Update:
{message}

Please open the Campus Help application to
view the complete request details.

Regards,
Campus Help Support Team
"""

    return send_email(
        recipient,
        email_subject,
        email_body.strip()
    )