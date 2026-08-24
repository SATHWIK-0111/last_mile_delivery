from datetime import date, datetime

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Text,
)

from app.database import Base


class RescheduleRequest(Base):
    __tablename__ = "reschedule_requests"

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

    old_date = Column(
        Date,
        nullable=True
    )

    new_date = Column(
        Date,
        nullable=False
    )

    reason = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )