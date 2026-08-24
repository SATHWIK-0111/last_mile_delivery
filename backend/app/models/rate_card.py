from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    UniqueConstraint,
)

from app.database import Base


class RateCard(Base):
    __tablename__ = "rate_cards"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    order_type = Column(
        String(10),
        nullable=False
    )

    zone_type = Column(
        String(10),
        nullable=False
    )

    base_rate = Column(
        Float,
        nullable=False
    )

    additional_rate = Column(
        Float,
        nullable=False
    )

    weight_limit = Column(
        Float,
        nullable=False,
        default=1.0
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

    __table_args__ = (
        UniqueConstraint(
            "order_type",
            "zone_type",
            name="uq_rate_card_type_zone"
        ),
    )