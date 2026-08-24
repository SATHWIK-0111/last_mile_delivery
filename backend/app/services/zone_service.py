import re
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.zone import Zone
from app.models.zone_area import ZoneArea


def normalize_text(value: str) -> str:
    """
    Normalize an address/area string so that
    matching is case-insensitive and punctuation
    does not interfere with detection.
    """
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9\s]", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value


def get_all_areas(db: Session):
    """
    Fetch all zone areas (joined with zone) once.
    Pass the result into detect_zone() when calling it
    more than once in the same request (e.g. pickup + drop)
    to avoid redundant queries.
    """
    return db.query(ZoneArea).join(Zone).all()


def detect_zone(
    address: str,
    db: Session,
    areas: list[ZoneArea] | None = None
) -> Zone:

    if not address or not address.strip():
        raise HTTPException(
            status_code=400,
            detail="Address cannot be empty"
        )

    normalized_address = normalize_text(address)

    if areas is None:
        areas = get_all_areas(db)

    # Prefer the longest matching area name.
    # This prevents smaller area names from winning
    # when a more specific area exists.
    matching_area = None
    longest_match_length = 0

    for area in areas:
        normalized_area = normalize_text(area.area_name)
        if not normalized_area:
            continue

        pattern = r"\b" + re.escape(normalized_area) + r"\b"

        if re.search(pattern, normalized_address):
            if len(normalized_area) > longest_match_length:
                matching_area = area
                longest_match_length = len(normalized_area)

    if not matching_area:
        raise HTTPException(
            status_code=400,
            detail=(
                "Could not determine delivery zone "
                "from the provided address"
            )
        )

    zone = (
        db.query(Zone)
        .filter(Zone.id == matching_area.zone_id)
        .first()
    )

    if not zone:
        raise HTTPException(
            status_code=500,
            detail="Zone configuration is invalid"
        )

    return zone