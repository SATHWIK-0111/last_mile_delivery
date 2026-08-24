from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)

from sqlalchemy.orm import relationship

from app.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    customer_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    pickup_address = Column(
        Text,
        nullable=False
    )
    pickup_latitude = Column(
        Float,
        nullable=True
    )

    pickup_longitude = Column(
        Float,
        nullable=True
    )
    drop_address = Column(
        Text,
        nullable=False
    )

    pickup_zone_id = Column(
        Integer,
        ForeignKey("zones.id"),
        nullable=False
    )

    drop_zone_id = Column(
        Integer,
        ForeignKey("zones.id"),
        nullable=False
    )

    length = Column(
        Float,
        nullable=False
    )

    breadth = Column(
        Float,
        nullable=False
    )

    height = Column(
        Float,
        nullable=False
    )

    actual_weight = Column(
        Float,
        nullable=False
    )

    volumetric_weight = Column(
        Float,
        nullable=False
    )

    billable_weight = Column(
        Float,
        nullable=False
    )

    order_type = Column(
        String(10),
        nullable=False
    )

    payment_type = Column(
        String(10),
        nullable=False
    )

    base_charge = Column(
        Float,
        nullable=False
    )

    cod_charge = Column(
        Float,
        nullable=False,
        default=0
    )

    total_charge = Column(
        Float,
        nullable=False
    )

    agent_id = Column(
        Integer,
        ForeignKey("agents.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    current_status = Column(
        String(30),
        nullable=False,
        default="CREATED"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    customer = relationship(
        "User",
        foreign_keys=[customer_id]
    )

    pickup_zone = relationship(
        "Zone",
        foreign_keys=[pickup_zone_id]
    )

    drop_zone = relationship(
        "Zone",
        foreign_keys=[drop_zone_id]
    )

    agent = relationship(
        "Agent",
        foreign_keys=[agent_id]
    )