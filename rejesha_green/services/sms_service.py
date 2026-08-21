import logging
import requests

from rejesha_green.config import settings


logger = logging.getLogger(__name__)


def format_sms_phone(phone: str) -> str:
    phone = phone.strip().replace(" ", "").replace("-", "").replace("+", "")

    if phone.startswith("0"):
        phone = "254" + phone[1:]
    elif phone.startswith("7"):
        phone = "254" + phone

    if not phone or not phone.startswith("2547") or len(phone) != 12:
        raise ValueError("Invalid Kenyan mobile phone number.")

    return phone


def send_sms(phone: str, message: str) -> bool:
    if not settings.SMS_API_KEY or not settings.SMS_API_SECRET:
        logger.error("SMS Leopard credentials are missing")
        return False

    if not settings.SMS_SENDER_ID:
        logger.error("SMS Leopard sender ID is missing")
        return False

    try:
        clean_phone = format_sms_phone(phone)
    except ValueError as exc:
        logger.error("Cannot send SMS: %s", exc)
        return False

    payload = {
        "source": settings.SMS_SENDER_ID,
        "message": message,
        "destination": [{"number": clean_phone}],
        "status_url": "",
        "status_secret": "",
    }

    headers = {
        "User-Agent": "Rejesha-Green-Backend/1.0",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            settings.SMS_API_URL,
            json=payload,
            headers=headers,
            auth=(settings.SMS_API_KEY, settings.SMS_API_SECRET),
            timeout=30,
        )

        logger.info(
            "SMS Leopard response: status=%s body=%s",
            response.status_code,
            response.text,
        )

        response.raise_for_status()

    except requests.HTTPError as exc:
        logger.error(
            "SMS Leopard HTTP error: status=%s body=%s",
            exc.response.status_code if exc.response else None,
            exc.response.text if exc.response else None,
        )
        return False

    except requests.RequestException as exc:
        logger.exception("SMS Leopard request failed: %s", exc)
        return False

    try:
        data = response.json()
    except ValueError:
        logger.error("SMS Leopard returned non-JSON response: %s", response.text)
        return False

    if not data.get("success", False):
        logger.error("SMS Leopard rejected SMS: %s", data)
        return False

    logger.info("SMS Leopard accepted SMS: phone=****%s", clean_phone[-4:])

    return True