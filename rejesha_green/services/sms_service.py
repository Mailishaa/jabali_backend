import logging
import requests
from rejesha_green.config import settings


logger = logging.getLogger(__name__)


def send_sms(phone: str, message: str) -> bool:
   if not settings.SMS_API_KEY or not settings.SMS_API_SECRET:
       logger.error("SMS Leopard credentials are missing")
       return False
   if not settings.SMS_SENDER_ID:
       logger.error("SMS Leopard sender ID is missing")
       return False
   clean_phone = phone.strip().replace(" ", "").replace("-", "").replace("+", "")
   if clean_phone.startswith("0"):
       clean_phone = "254" + clean_phone[1:]
   if not clean_phone:
       logger.error("Cannot send SMS: phone number is empty")
       return False
   payload = {"source": settings.SMS_SENDER_ID, "message": message, "destination": [{"number": clean_phone}], "status_url": "", "status_secret": ""}
   headers = {"User-Agent": "Rejesha-Green-Backend/1.0", "Accept": "application/json", "Content-Type": "application/json"}
   try:
       response = requests.post(settings.SMS_API_URL, json=payload, headers=headers, auth=(settings.SMS_API_KEY, settings.SMS_API_SECRET), timeout=30)
       logger.info("SMS LEOPARD RESPONSE: status=%s body=%s", response.status_code, response.text)
       response.raise_for_status()
   except requests.HTTPError as exc:
       logger.error("SMS Leopard HTTP error: status=%s body=%s", exc.response.status_code if exc.response else None, exc.response.text if exc.response else None)
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
   logger.info("SMS LEOPARD ACCEPTED SMS: phone=****%s", clean_phone[-4:])
   return True
