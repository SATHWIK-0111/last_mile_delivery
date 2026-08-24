from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class ZoneArea(Base):
    __tablename__ = "zone_areas"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    zone_id = Column(
        Integer,
        ForeignKey("zones.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    area_name = Column(
        String(150),
        nullable=False,
        index=True
    )

    zone = relationship(
        "Zone",
        back_populates="areas"
    )