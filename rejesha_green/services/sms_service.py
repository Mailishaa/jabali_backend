# # forest_activities
# import logging
# # dev
# import requests

# from rejesha_green.config import settings


# class SMSService:

#     def send_sms(
#         self,
#         phone_number: str,
#         message: str,
#     ) -> dict:

#         response = requests.post(
#             settings.SMS_API_URL,
#             auth=(
#                 settings.SMS_API_KEY,
#                 settings.SMS_API_SECRET,
#             ),
#             headers={
#                 "Content-Type": "application/json",
#             },
#             json={
#                 "source": settings.SMS_SENDER_ID,
#                 "multi": False,
#                 "message": message,
#                 "destination": [
#                     {
#                         "number": phone_number,
#                     }
#                 ],
#             },
#             timeout=30,
#         )

#         response.raise_for_status()

#         return response.json()

#     def send_bulk_sms(
#         self,
#         phone_numbers: list[str],
#         message: str,
#     ) -> list[dict]:

#         results = []

#         for phone_number in phone_numbers:
#             try:
#                 response = self.send_sms(
#                     phone_number=phone_number,
#                     message=message,
#                 )

#                 results.append(
#                     {
#                         "phone_number": phone_number,
#                         "success": True,
#                         "response": response,
#                     }
#                 )

#             except requests.RequestException as error:
#                 results.append(
#                     {
#                         "phone_number": phone_number,
#                         "success": False,
#                         "error": str(error),
#                     }
#                 )

#         return results
# logger = logging.getLogger(__name__)


# def format_sms_phone(phone: str) -> str:
#     phone = phone.strip().replace(" ", "").replace("-", "").replace("+", "")

#     if phone.startswith("0"):
#         phone = "254" + phone[1:]
#     elif phone.startswith("7"):
#         phone = "254" + phone

#     if not phone or not phone.startswith("2547") or len(phone) != 12:
#         raise ValueError("Invalid Kenyan mobile phone number.")

#     return phone


# def send_sms(phone: str, message: str) -> bool:
#     if not settings.SMS_API_KEY or not settings.SMS_API_SECRET:
#         logger.error("SMS Leopard credentials are missing")
#         return False

#     if not settings.SMS_SENDER_ID:
#         logger.error("SMS Leopard sender ID is missing")
#         return False

#     try:
#         clean_phone = format_sms_phone(phone)
#     except ValueError as exc:
#         logger.error("Cannot send SMS: %s", exc)
#         return False

#     payload = {
#         "source": settings.SMS_SENDER_ID,
#         "message": message,
#         "destination": [{"number": clean_phone}],
#         "status_url": "",
#         "status_secret": "",
#     }

#     headers = {
#         "User-Agent": "Rejesha-Green-Backend/1.0",
#         "Accept": "application/json",
#         "Content-Type": "application/json",
#     }

#     try:
#         response = requests.post(
#             settings.SMS_API_URL,
#             json=payload,
#             headers=headers,
#             auth=(settings.SMS_API_KEY, settings.SMS_API_SECRET),
#             timeout=30,
#         )

#         logger.info(
#             "SMS Leopard response: status=%s body=%s",
#             response.status_code,
#             response.text,
#         )

#         response.raise_for_status()

#     except requests.HTTPError as exc:
#         logger.error(
#             "SMS Leopard HTTP error: status=%s body=%s",
#             exc.response.status_code if exc.response else None,
#             exc.response.text if exc.response else None,
#         )
#         return False

#     except requests.RequestException as exc:
#         logger.exception("SMS Leopard request failed: %s", exc)
#         return False

#     try:
#         data = response.json()
#     except ValueError:
#         logger.error("SMS Leopard returned non-JSON response: %s", response.text)
#         return False

#     if not data.get("success", False):
#         logger.error("SMS Leopard rejected SMS: %s", data)
#         return False

#     logger.info("SMS Leopard accepted SMS: phone=****%s", clean_phone[-4:])

#     return True  


import logging
import requests

from rejesha_green.config import settings


logger = logging.getLogger(__name__)


class SMSService:

    @staticmethod
    def format_phone(phone: str) -> str:
        """
        Convert a Kenyan phone number to international format.

        Examples:
            0712345678   -> 254712345678
            +254712345678 -> 254712345678
            254712345678 -> 254712345678
            712345678    -> 254712345678
        """

        phone = (
            phone.strip()
            .replace(" ", "")
            .replace("-", "")
            .replace("+", "")
        )

        if phone.startswith("0"):
            phone = "254" + phone[1:]

        elif phone.startswith("7"):
            phone = "254" + phone

        if not phone.startswith("2547") or len(phone) != 12:
            raise ValueError("Invalid Kenyan mobile phone number.")

        return phone

    @staticmethod
    def send_sms(
        phone_number: str,
        message: str,
    ) -> bool:
        """
        Send one SMS using SMS Leopard.
        Returns True if SMS was accepted, otherwise False.
        """

        # Check SMS configuration
        if not settings.SMS_API_KEY:
            logger.error("SMS API key is missing.")
            return False

        if not settings.SMS_API_SECRET:
            logger.error("SMS API secret is missing.")
            return False

        if not settings.SMS_SENDER_ID:
            logger.error("SMS sender ID is missing.")
            return False

        # Format phone number
        try:
            clean_phone = SMSService.format_phone(phone_number)

        except ValueError as exc:
            logger.error("Invalid phone number: %s", exc)
            return False

        # SMS Leopard payload
        payload = {
            "source": settings.SMS_SENDER_ID,
            "message": message,
            "destination": [
                {
                    "number": clean_phone
                }
            ],
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
                auth=(
                    settings.SMS_API_KEY,
                    settings.SMS_API_SECRET,
                ),
                timeout=30,
            )

            logger.info(
                "SMS Leopard response: status=%s",
                response.status_code,
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
            logger.exception(
                "SMS Leopard request failed: %s",
                exc,
            )
            return False

        # Parse response
        try:
            data = response.json()

        except ValueError:
            logger.error(
                "SMS Leopard returned non-JSON response: %s",
                response.text,
            )
            return False

        # Check SMS Leopard response
        if not data.get("success", False):
            logger.error(
                "SMS Leopard rejected SMS: %s",
                data,
            )
            return False

        logger.info(
            "SMS sent successfully to ****%s",
            clean_phone[-4:],
        )

        return True

    @staticmethod
    def send_bulk_sms(
        phone_numbers: list[str],
        message: str,
    ) -> list[dict]:
        """
        Send the same SMS to multiple phone numbers.
        """

        results = []

        for phone_number in phone_numbers:

            success = SMSService.send_sms(
                phone_number=phone_number,
                message=message,
            )

            results.append(
                {
                    "phone_number": phone_number,
                    "success": success,
                }
            )

        return results

