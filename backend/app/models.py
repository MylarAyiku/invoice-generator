from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.sql import func
from .database import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String, unique=True, index=True)

    # Sender info
    sender_name = Column(String, nullable=False)
    sender_email = Column(String, nullable=False)
    sender_address = Column(String, nullable=False)

    # Client info
    client_name = Column(String, nullable=False)
    client_email = Column(String, nullable=False)
    client_address = Column(String, nullable=False)

    # Invoice details
    items = Column(JSON, nullable=False)  # list of {description, quantity, unit_price}
    subtotal = Column(Float, nullable=False)
    tax_rate = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    total = Column(Float, nullable=False)

    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())