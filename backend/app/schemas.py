from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class InvoiceItem(BaseModel):
    description: str
    quantity: float
    unit_price: float

class InvoiceCreate(BaseModel):
    sender_name: str
    sender_email: str
    sender_address: str
    client_name: str
    client_email: str
    client_address: str
    items: List[InvoiceItem]
    tax_rate: Optional[float] = 0.0
    notes: Optional[str] = None

class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    sender_name: str
    sender_email: str
    sender_address: str
    client_name: str
    client_email: str
    client_address: str
    items: list
    subtotal: float
    tax_rate: float
    tax_amount: float
    total: float
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True