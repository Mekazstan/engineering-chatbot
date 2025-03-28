import os
import httpx
from config import Config

# Mailgun Configuration
MAILGUN_API_KEY = Config.MAILGUN_API_KEY
MAILGUN_DOMAIN = Config.MAILGUN_DOMAIN
FROM_EMAIL = f"Engineering Support <no-reply@{MAILGUN_DOMAIN}>"

async def send_mailgun_email(recipients: list[str], subject: str, html: str):
    """Send email using Mailgun API"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
                auth=("api", MAILGUN_API_KEY),
                data={
                    "from": FROM_EMAIL,
                    "to": recipients,
                    "subject": subject,
                    "html": html
                },
                timeout=10.0
            )
            response.raise_for_status()
            return True
        except httpx.HTTPStatusError as e:
            print(f"Mailgun API error: {e.response.text}")
            return False
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
        