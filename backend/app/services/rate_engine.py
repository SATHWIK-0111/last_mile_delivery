from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.cod_charge import CodCharge
from app.models.rate_card import RateCard
from app.services.zone_service import detect_zone, get_all_areas


VOLUMETRIC_DIVISOR = 5000


def calculate_volumetric_weight(length: float, breadth: float, height: float) -> float:
    if length <= 0 or breadth <= 0 or height <= 0:
        raise HTTPException(
            status_code=400,
            detail="Package dimensions must be greater than zero"
        )
    return length * breadth * height / VOLUMETRIC_DIVISOR


def calculate_rate(
    *,
    pickup_address: str,
    drop_address: str,
    length: float,
    breadth: float,
    height: float,
    actual_weight: float,
    order_type: str,
    payment_type: str,
    db: Session
) -> dict:

    # 1. Validate inputs
    order_type = order_type.upper()
    payment_type = payment_type.upper()

    if order_type not in {"B2B", "B2C"}:
        raise HTTPException(status_code=400, detail="order_type must be B2B or B2C")

    if payment_type not in {"PREPAID", "COD"}:
        raise HTTPException(status_code=400, detail="payment_type must be PREPAID or COD")

    if actual_weight <= 0:
        raise HTTPException(status_code=400, detail="Actual weight must be greater than zero")

    # 2. Detect zones — fetch areas ONCE, reuse for both lookups
    areas = get_all_areas(db)
    pickup_zone = detect_zone(pickup_address, db, areas=areas)
    drop_zone = detect_zone(drop_address, db, areas=areas)

    # 3. Determine intra/inter
    zone_type = "INTRA" if pickup_zone.id == drop_zone.id else "INTER"

    # 4. Volumetric weight
    volumetric_weight = calculate_volumetric_weight(length, breadth, height)

    # 5. Billable weight
    billable_weight = max(actual_weight, volumetric_weight)

    # 6. Find rate card
    rate_card = (
        db.query(RateCard)
        .filter(
            RateCard.order_type == order_type,
            RateCard.zone_type == zone_type
        )
        .first()
    )

    if not rate_card:
        raise HTTPException(
            status_code=400,
            detail=f"No rate card configured for {order_type} / {zone_type}"
        )

    # 6b. Guard against incomplete admin configuration
    if rate_card.weight_limit is None or rate_card.base_rate is None:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Rate card for {order_type} / {zone_type} is missing "
                "weight_limit or base_rate — admin must complete this "
                "rate card before it can be used"
            )
        )

    # 7. Base charge
    if billable_weight <= rate_card.weight_limit:
        base_charge = rate_card.base_rate
    else:
        if rate_card.additional_rate is None:
            raise HTTPException(
                status_code=500,
                detail=(
                    f"Rate card for {order_type} / {zone_type} is missing "
                    "additional_rate, required for weights above "
                    f"{rate_card.weight_limit}kg"
                )
            )
        extra_weight = billable_weight - rate_card.weight_limit
        base_charge = rate_card.base_rate + (extra_weight * rate_card.additional_rate)

    # 8. COD surcharge
    cod_charge = 0.0
    if payment_type == "COD":
        cod_config = (
            db.query(CodCharge)
            .filter(CodCharge.order_type == order_type)
            .first()
        )
        if not cod_config:
            raise HTTPException(
                status_code=400,
                detail=f"No COD charge configured for {order_type}"
            )
        cod_charge = cod_config.charge

    # 9. Final charge
    total_charge = base_charge + cod_charge

    return {
        "pickup_zone_id": pickup_zone.id,
        "pickup_zone": pickup_zone.name,
        "drop_zone_id": drop_zone.id,
        "drop_zone": drop_zone.name,
        "zone_type": zone_type,
        "actual_weight": round(actual_weight, 2),
        "volumetric_weight": round(volumetric_weight, 2),
        "billable_weight": round(billable_weight, 2),
        "order_type": order_type,
        "payment_type": payment_type,
        "rate_card_id": rate_card.id,
        "base_charge": round(base_charge, 2),
        "cod_charge": round(cod_charge, 2),
        "total_charge": round(total_charge, 2)
    }