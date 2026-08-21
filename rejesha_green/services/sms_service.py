import requests

from rejesha_green.config import settings


class SMSService:

    def send_sms(
        self,
        phone_number: str,
        message: str,
    ) -> dict:

        response = requests.post(
            settings.SMS_API_URL,
            auth=(
                settings.SMS_API_KEY,
                settings.SMS_API_SECRET,
            ),
            headers={
                "Content-Type": "application/json",
            },
            json={
                "source": settings.SMS_SENDER_ID,
                "multi": False,
                "message": message,
                "destination": [
                    {
                        "number": phone_number,
                    }
                ],
            },
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    def send_bulk_sms(
        self,
        phone_numbers: list[str],
        message: str,
    ) -> list[dict]:

        results = []

        for phone_number in phone_numbers:
            try:
                response = self.send_sms(
                    phone_number=phone_number,
                    message=message,
                )

                results.append(
                    {
                        "phone_number": phone_number,
                        "success": True,
                        "response": response,
                    }
                )

            except requests.RequestException as error:
                results.append(
                    {
                        "phone_number": phone_number,
                        "success": False,
                        "error": str(error),
                    }
                )

        return results