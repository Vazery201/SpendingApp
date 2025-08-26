import requests
from typing import Dict, Any
from .config import get_settings, plaid_base_url

settings = get_settings()
BASE = plaid_base_url(settings.PLAID_ENV)

def _auth() -> Dict[str, str]:
    return {"client_id": settings.PLAID_CLIENT_ID, "secret": settings.PLAID_SECRET}

def create_link_token(client_user_id: str) -> Dict[str, Any]:
    url = f"{BASE}/link/token/create"
    payload = {
        **_auth(),
        "user": {"client_user_id": client_user_id},
        "client_name": settings.APP_NAME,
        "products": ["transactions"],
        "country_codes": ["CA", "US"],
        "language": "en",
    }
    r = requests.post(url, json=payload, timeout=20)
    r.raise_for_status()
    return r.json()

def exchange_public_token(public_token: str) -> Dict[str, Any]:
    url = f"{BASE}/item/public_token/exchange"
    payload = {**_auth(), "public_token": public_token}
    r = requests.post(url, json=payload, timeout=20)
    if r.status_code != 200:
        try:
            return {"_debug_status": r.status_code, "_debug_body": r.json()}
        except Exception:
            return {"_debug_status": r.status_code, "_debug_body": r.text}
    return r.json()

def get_transactions(access_token: str, start_date: str, end_date: str, count: int = 100, offset: int = 0) -> Dict[str, Any]:
    url = f"{BASE}/transactions/get"
    payload = {
        **_auth(),
        "access_token": access_token,
        "start_date": start_date,
        "end_date": end_date,
        "options": {"count": count, "offset": offset},
    }
    r = requests.post(url, json=payload, timeout=30)
    if r.status_code != 200:
        try:
            return {"_debug_status": r.status_code, "_debug_body": r.json()}
        except Exception:
            return {"_debug_status": r.status_code, "_debug_body": r.text}
    return r.json()


def sandbox_public_token_create(institution_id: str = "ins_109508"):
    url = f"{BASE}/sandbox/public_token/create"
    payload = {**_auth(), "institution_id": institution_id, "initial_products": ["transactions"]}
    r = requests.post(url, json=payload, timeout=20)
    r.raise_for_status()
    return r.json()
