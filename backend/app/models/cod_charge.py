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


class CodCharge(Base):
    __tablename__ = "cod_charges"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    order_type = Column(
        String(10),
        nullable=False
    )

    charge = Column(
        Float,
        nullable=False
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
            name="uq_cod_charge_order_type"
        ),
    )