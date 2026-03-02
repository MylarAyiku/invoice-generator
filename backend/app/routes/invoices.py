from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Invoice
from ..schemas import InvoiceCreate, InvoiceResponse
import random
import string

router = APIRouter()


def generate_invoice_number():
    chars = string.ascii_uppercase + string.digits
    suffix = ''.join(random.choices(chars, k=6))
    return f"INV-{suffix}"


def calculate_totals(items, tax_rate):
    subtotal = sum(item.quantity * item.unit_price for item in items)
    tax_amount = subtotal * (tax_rate / 100)
    total = subtotal + tax_amount
    return subtotal, tax_amount, total


@router.post("/", response_model=InvoiceResponse)
def create_invoice(invoice: InvoiceCreate, db: Session = Depends(get_db)):
    subtotal, tax_amount, total = calculate_totals(invoice.items, invoice.tax_rate)

    db_invoice = Invoice(
        invoice_number=generate_invoice_number(),
        sender_name=invoice.sender_name,
        sender_email=invoice.sender_email,
        sender_address=invoice.sender_address,
        client_name=invoice.client_name,
        client_email=invoice.client_email,
        client_address=invoice.client_address,
        items=[item.model_dump() for item in invoice.items],
        subtotal=subtotal,
        tax_rate=invoice.tax_rate,
        tax_amount=tax_amount,
        total=total,
        notes=invoice.notes
    )
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice


@router.get("/", response_model=List[InvoiceResponse])
def get_invoices(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return db.query(Invoice).order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice