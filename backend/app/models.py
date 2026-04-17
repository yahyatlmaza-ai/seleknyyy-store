"""SQLModel definitions for auto Flow.

Multi-tenant: every row that belongs to a company has a `tenant_id` column.
All reads/writes MUST filter on tenant_id via the dependencies in deps.py.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlmodel import Field, SQLModel

from .config import TRIAL_DAYS


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def trial_end_default() -> datetime:
    return utcnow() + timedelta(days=TRIAL_DAYS)


# ---------------------------------------------------------------------------
# Tenants + Users
# ---------------------------------------------------------------------------


class Tenant(SQLModel, table=True):
    __tablename__ = "tenants"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    slug: str = Field(index=True, unique=True)
    plan: str = Field(default="trial")  # trial | starter | professional | vip | expired
    trial_end: datetime = Field(default_factory=trial_end_default)
    subscription_end: Optional[datetime] = None
    created_at: datetime = Field(default_factory=utcnow)


class User(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenants.id", index=True)
    email: str = Field(index=True, unique=True)
    password_hash: str
    full_name: str = ""
    phone: str = ""
    role: str = Field(default="owner")  # owner | admin | staff
    email_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=utcnow)
    last_login_at: Optional[datetime] = None


class OTPSession(SQLModel, table=True):
    __tablename__ = "otp_sessions"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    code_hash: str
    purpose: str = Field(default="verify_email")  # verify_email | reset_password
    expires_at: datetime
    consumed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=utcnow)


# ---------------------------------------------------------------------------
# Customers
# ---------------------------------------------------------------------------


class Customer(SQLModel, table=True):
    __tablename__ = "customers"
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenants.id", index=True)
    name: str
    phone: str = ""
    email: str = ""
    address: str = ""
    city: str = ""
    notes: str = ""
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


# ---------------------------------------------------------------------------
# Delivery agents
# ---------------------------------------------------------------------------


class DeliveryAgent(SQLModel, table=True):
    __tablename__ = "delivery_agents"
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenants.id", index=True)
    name: str
    phone: str = ""
    zone: str = ""  # city / region
    active: bool = Field(default=True)
    delivered_count: int = Field(default=0)
    failed_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=utcnow)


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------


ORDER_STATUSES = ("pending", "confirmed", "shipped", "delivered", "cancelled")

# Allowed transitions. Keys are current status, values are the statuses you
# can move TO from that current status.
ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "pending": {"confirmed", "cancelled"},
    "confirmed": {"shipped", "cancelled"},
    "shipped": {"delivered", "cancelled"},
    "delivered": set(),
    "cancelled": set(),
}


class Order(SQLModel, table=True):
    __tablename__ = "orders"
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenants.id", index=True)
    reference: str = Field(index=True)  # tenant-scoped human reference
    customer_id: Optional[int] = Field(default=None, foreign_key="customers.id")
    agent_id: Optional[int] = Field(default=None, foreign_key="delivery_agents.id")
    status: str = Field(default="pending", index=True)
    product_name: str
    quantity: int = Field(default=1)
    price: float = Field(default=0.0)
    currency: str = Field(default="DZD")
    shipping_address: str = ""
    shipping_city: str = ""
    notes: str = ""
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class OrderStatusHistory(SQLModel, table=True):
    __tablename__ = "order_status_history"
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenants.id", index=True)
    order_id: int = Field(foreign_key="orders.id", index=True)
    from_status: Optional[str] = None
    to_status: str
    changed_by_user_id: Optional[int] = None
    note: str = ""
    created_at: datetime = Field(default_factory=utcnow)


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------


class Notification(SQLModel, table=True):
    __tablename__ = "notifications"
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenants.id", index=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    kind: str  # order_created | order_status | trial_expiring | trial_expired | generic
    title: str
    body: str = ""
    related_order_id: Optional[int] = None
    read: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=utcnow)
