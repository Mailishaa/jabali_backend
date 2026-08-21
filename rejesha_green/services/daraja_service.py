import base64
from datetime import datetime

import requests

from rejesha_green.config import settings


def get_base_url() -> str:
    return "https://api.safaricom.co.ke" if settings.MPESA_ENVIRONMENT == "production" else "https://sandbox.safaricom.co.ke"


def format_mpesa_phone(phone: str) -> str:
    phone = phone.strip().replace(" ", "").replace("-", "").replace("+", "")

    if phone.startswith("0"):
        phone = "254" + phone[1:]
    elif phone.startswith("7"):
        phone = "254" + phone
    elif not phone.startswith("254"):
        raise ValueError("Invalid Kenyan phone number. Use 0712345678 or 254712345678.")

    if len(phone) != 12 or not phone.startswith("2547"):
        raise ValueError("Invalid Kenyan mobile phone number.")

    return phone


def get_access_token() -> str:
    url = f"{get_base_url()}/oauth/v1/generate?grant_type=client_credentials"

    response = requests.get(
        url,
        auth=(settings.DARAJA_CONSUMER_KEY, settings.DARAJA_CONSUMER_SECRET),
        timeout=30,
    )

    response.raise_for_status()

    return response.json()["access_token"]


def stk_push(phone: str, amount: int):
    phone = format_mpesa_phone(phone)
    access_token = get_access_token()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    password = base64.b64encode(
        f"{settings.DARAJA_SHORTCODE}{settings.DARAJA_PASSKEY}{timestamp}".encode()
    ).decode()

    payload = {
        "BusinessShortCode": settings.DARAJA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": settings.DARAJA_SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": settings.DARAJA_CALLBACK_URL,
        "AccountReference": "JABALI-REG",
        "TransactionDesc": "JABALI Registration",
    }

    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    url = f"{get_base_url()}/mpesa/stkpush/v1/processrequest"

    response = requests.post(url, json=payload, headers=headers, timeout=30)

    if not response.ok:
        raise Exception(f"Daraja STK Push failed: {response.status_code} {response.text}")

    return response.json()