from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Text,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


# ---------- USER (for auth) ----------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=True)  # null for google-only later
    google_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ---------- CUSTOMER ----------
class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String)
    phone = Column(String)
    address = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    invoices = relationship("Invoice", back_populates="customer")


# ---------- PRODUCT ----------
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    sku = Column(String, unique=True)
    name = Column(String, nullable=False)
    unit_price = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    invoice_items = relationship("InvoiceItem", back_populates="product")


# ---------- INVOICE ----------
class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True)
    invoice_number = Column(String, unique=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)

    total = Column(Float)
    currency = Column(String, default="INR")
    issue_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice")


# ---------- INVOICE ITEMS ----------
class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)

    description = Column(Text)
    quantity = Column(Float, default=1)
    unit_price = Column(Float, default=0.0)
    line_total = Column(Float, default=0.0)

    invoice = relationship("Invoice", back_populates="items")
    product = relationship("Product", back_populates="invoice_items")


# ---------- EXPENSE ----------
class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True)
    original_text = Column(Text)
    amount = Column(Float)
    currency = Column(String, default="INR")
    vendor = Column(String)
    category = Column(String)
    confidence = Column(Float)
    date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
