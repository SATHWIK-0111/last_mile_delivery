from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.services.notification_service import create_notification
from app.models.order import Order
from app.models.agent import Agent
from app.services.tracking_service import add_event


# ==========================================
# VALID STATUS TRANSITIONS
# ==========================================

VALID_TRANSITIONS = {
    "CREATED": {"ASSIGNED"},
    "ASSIGNED": {"PICKED_UP"},
    "PICKED_UP": {"IN_TRANSIT"},
    "IN_TRANSIT": {"OUT_FOR_DELIVERY"},
    "OUT_FOR_DELIVERY": {
        "DELIVERED",
        "FAILED"
    },
    "DELIVERED": set(),
    "FAILED": {"RESCHEDULED"},
    "RESCHEDULED": {"ASSIGNED"},
}


def update_order_status(
    *,
    order_id: int,
    new_status: str,
    actor_id: int,
    actor_role: str,
    db: Session
) -> Order:

    # -----------------------------------------
    # 1. Normalize status
    # -----------------------------------------

    new_status = new_status.upper().strip()

    allowed_statuses = {
        "CREATED",
        "ASSIGNED",
        "PICKED_UP",
        "IN_TRANSIT",
        "OUT_FOR_DELIVERY",
        "DELIVERED",
        "FAILED",
        "RESCHEDULED",
    }

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status: {new_status}"
        )

    # -----------------------------------------
    # 2. Get order
    # -----------------------------------------

    order = db.get(
        Order,
        order_id
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    current_status = order.current_status

    # -----------------------------------------
    # 3. Check transition
    # -----------------------------------------

    allowed_next_statuses = VALID_TRANSITIONS.get(
        current_status,
        set()
    )

    if new_status not in allowed_next_statuses:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid status transition: "
                f"{current_status} -> {new_status}"
            )
        )

    # -----------------------------------------
    # 4. Update order status
    # -----------------------------------------

    order.current_status = new_status

    # -----------------------------------------
    # 5. Free agent after delivery
    #    or failed delivery
    # -----------------------------------------

    if (
        new_status in {"DELIVERED", "FAILED"}
        and order.agent_id is not None
    ):

        agent = db.get(
            Agent,
            order.agent_id
        )

        if agent:
            agent.availability_status = "AVAILABLE"

    # -----------------------------------------
    # 6. Create tracking history
    # -----------------------------------------

    add_event(
        order_id=order.id,
        status=new_status,
        actor_id=actor_id,
        actor_role=actor_role,
        remarks=(
            f"Order status changed from "
            f"{current_status} to {new_status}"
        ),
        db=db
    )

    # -----------------------------------------
    # 7. Customer notification for failure
    # -----------------------------------------

    if new_status == "FAILED":

        create_notification(
            order_id=order.id,
            recipient_id=order.customer_id,
            channel="EMAIL",
            event_type="DELIVERY_FAILED",
            db=db
        )

    # -----------------------------------------
    # 8. Save everything
    # -----------------------------------------

    db.commit()
    db.refresh(order)

    return order


def fail_order(
    *,
    order_id: int,
    actor_id: int,
    actor_role: str,
    reason: str,
    db: Session
) -> Order:

    # -----------------------------------------
    # 1. Validate failure reason
    # -----------------------------------------

    reason = reason.strip()

    if not reason:
        raise HTTPException(
            status_code=400,
            detail="Failure reason is required"
        )

    # -----------------------------------------
    # 2. Get order
    # -----------------------------------------

    order = db.get(
        Order,
        order_id
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    current_status = order.current_status

    # -----------------------------------------
    # 3. Validate current status
    # -----------------------------------------

    if current_status != "OUT_FOR_DELIVERY":
        raise HTTPException(
            status_code=400,
            detail=(
                "Order can only be marked FAILED "
                "when it is OUT_FOR_DELIVERY"
            )
        )

    # -----------------------------------------
    # 4. Update order status
    # -----------------------------------------

    order.current_status = "FAILED"

    # -----------------------------------------
    # 5. Free the agent
    # -----------------------------------------

    if order.agent_id is not None:

        agent = db.get(
            Agent,
            order.agent_id
        )

        if agent:
            agent.availability_status = "AVAILABLE"

    # -----------------------------------------
    # 6. Create tracking history
    # -----------------------------------------

    add_event(
        order_id=order.id,
        status="FAILED",
        actor_id=actor_id,
        actor_role=actor_role,
        remarks=reason,
        db=db
    )

    # -----------------------------------------
    # 7. Notify customer
    # -----------------------------------------

    create_notification(
        order_id=order.id,
        recipient_id=order.customer_id,
        channel="EMAIL",
        event_type="DELIVERY_FAILED",
        db=db
    )

    # -----------------------------------------
    # 8. Save everything
    # -----------------------------------------

    db.commit()
    db.refresh(order)

    return order