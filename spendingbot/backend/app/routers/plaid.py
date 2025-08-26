from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import date, timedelta
from typing import Dict
from ..plaid_http import (
    create_link_token,
    exchange_public_token,
    get_transactions,
    sandbox_public_token_create,
)

router = APIRouter(prefix="/plaid", tags=["plaid"])

# In-memory demo storage for Week 1 (DO NOT use in prod)
# key = client_user_id -> access_token
_ACCESS_TOKENS: Dict[str, str] = {}

@router.post("/create_link_token")
def api_create_link_token(client_user_id: str = "demo-user"):
    try:
        resp = create_link_token(client_user_id)
        return {"link_token": resp.get("link_token")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"link_token error: {e}")

@router.post("/sandbox_public_token")
def api_sandbox_public_token(institution_id: str = "ins_109508"):
    """Generate a sandbox public_token (simulates finishing Plaid Link)."""
    try:
        resp = sandbox_public_token_create(institution_id)
        return {"public_token": resp.get("public_token")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"sandbox_public_token error: {e}")

class ExchangeRequest(BaseModel):
    public_token: str

@router.post("/exchange_public_token")
def api_exchange_public_token(payload: ExchangeRequest, client_user_id: str = "demo-user"):
    try:
        resp = exchange_public_token(payload.public_token)
        access_token = resp.get("access_token")
        item_id = resp.get("item_id")
        if not access_token:
            raise ValueError("no access_token returned")
        # Week 1 demo: stash in-memory so we can fetch txns
        _ACCESS_TOKENS[client_user_id] = access_token
        # ⚠️ Week 1 only: return access_token so you can test; NEVER do this in prod.
        return {"item_id": item_id, "access_token": access_token}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"exchange error: {e}")

@router.get("/transactions")
def api_transactions(client_user_id: str = "demo-user", days: int = 30):
    try:
        access_token = _ACCESS_TOKENS.get(client_user_id)
        if not access_token:
            raise HTTPException(status_code=400, detail="No access_token for this user yet. Link account first.")
        end = date.today()
        start = end - timedelta(days=days)
        resp = get_transactions(access_token, start.isoformat(), end.isoformat())
        # Bubble Plaid error details if present
        if "_debug_status" in resp:
            return resp
        return {"total": resp.get("total_transactions", 0), "transactions": resp.get("transactions", [])}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"transactions error: {e}")
