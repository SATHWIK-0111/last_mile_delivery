from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.order import Order
from app.services.tracking_service import add_event
from app.models.user import User
from app.services.rate_engine import calculate_rate


def create_order(
    *,
    customer_id: int,
    actor_id: int,
    actor_role: str,
    pickup_address: str,
    pickup_latitude: float | None,
    pickup_longitude: float | None,
    drop_address: str,
    length: float,
    breadth: float,
    height: float,
    actual_weight: float,
    order_type: str,
    payment_type: str,
    db: Session
) -> Order:

    # -----------------------------------------
    # 1. Verify customer
    # -----------------------------------------

    customer = db.get(
        User,
        customer_id
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    if customer.role != "CUSTOMER":
        raise HTTPException(
            status_code=400,
            detail="Selected user is not a customer"
        )

    # -----------------------------------------
    # 2. Calculate charge
    # -----------------------------------------

    calculation = calculate_rate(
        pickup_address=pickup_address,
        drop_address=drop_address,
        length=length,
        breadth=breadth,
        height=height,
        actual_weight=actual_weight,
        order_type=order_type,
        payment_type=payment_type,
        db=db
    )

    # -----------------------------------------
    # 3. Create order
    # -----------------------------------------

    order = Order(
        customer_id=customer_id,

        pickup_address=pickup_address,
        pickup_latitude=pickup_latitude,
        pickup_longitude=pickup_longitude,

        drop_address=drop_address,

        pickup_zone_id=calculation[
            "pickup_zone_id"
        ],

        drop_zone_id=calculation[
            "drop_zone_id"
        ],

        length=length,
        breadth=breadth,
        height=height,

        actual_weight=calculation[
            "actual_weight"
        ],

        volumetric_weight=calculation[
            "volumetric_weight"
        ],

        billable_weight=calculation[
            "billable_weight"
        ],

        order_type=calculation[
            "order_type"
        ],

        payment_type=calculation[
            "payment_type"
        ],

        base_charge=calculation[
            "base_charge"
        ],

        cod_charge=calculation[
            "cod_charge"
        ],

        total_charge=calculation[
            "total_charge"
        ],

        current_status="CREATED"
    )

    db.add(order)

    # We need the generated order ID
    # before creating tracking history.
    db.flush()

    # -----------------------------------------
    # 4. Initial tracking event
    # -----------------------------------------

    add_event(
        order_id=order.id,
        status="CREATED",
        actor_id=actor_id,
        actor_role=actor_role,
        remarks="Order created",
        db=db
    )

    db.commit()
    db.refresh(order)

    return order