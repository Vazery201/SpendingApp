from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class User(SQLModel, table=True):
    id: str = Field(primary_key=True)  # e.g., "demo-user"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    item_id: str = Field(index=True)             # Plaid item_id
    access_token_enc: str                        # encrypted access_token
    institution_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Account(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    item_id: str = Field(index=True)
    account_id: str = Field(index=True)          # Plaid account_id
    name: Optional[str] = None
    mask: Optional[str] = None
    official_name: Optional[str] = None
    type: Optional[str] = None
    subtype: Optional[str] = None

class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    account_id: str = Field(index=True)
    transaction_id: str = Field(index=True, unique=True)
    name: Optional[str] = None
    amount: float
    currency: Optional[str] = "CAD"
    date: str = Field(index=True)  # YYYY-MM-DD
    category_primary: Optional[str] = None       # from Plaid categories[0] if present
    raw: Optional[str] = None                    # JSON dump if you want
