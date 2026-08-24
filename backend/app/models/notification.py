from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)

from app.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    order_id = Column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    recipient_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    channel = Column(
        String(10),
        nullable=False
    )

    event_type = Column(
        String(30),
        nullable=False
    )

    sent_at = Column(
        DateTime,
        nullable=True
    )

    status = Column(
        String(20),
        nullable=False,
        default="PENDING"
    )