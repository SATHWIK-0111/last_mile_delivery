from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)

from app.database import Base


class DeliveryAssignment(Base):
    __tablename__ = "delivery_assignments"

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

    agent_id = Column(
        Integer,
        ForeignKey("agents.id"),
        nullable=False,
        index=True
    )

    assigned_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    assignment_type = Column(
        String(20),
        nullable=False
    )

    assigned_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )