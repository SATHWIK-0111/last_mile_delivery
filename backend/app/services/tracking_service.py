from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.tracking_history import TrackingHistory


def add_event(
    *,
    order_id: int,
    status: str,
    actor_id: int | None,
    actor_role: str | None,
    remarks: str | None,
    db: Session
) -> TrackingHistory:
    """
    Add a tracking event for an order.

    This is the single entry point for creating
    tracking history records.
    """

    event = TrackingHistory(
        order_id=order_id,
        status=status,
        actor_id=actor_id,
        actor_role=actor_role,
        remarks=remarks
    )

    db.add(event)

    return event


def get_order_tracking(
    *,
    order_id: int,
    db: Session
) -> dict:
    """
    Return the current order status and complete
    tracking history.
    """

    order = db.get(Order, order_id)

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    history = (
        db.query(TrackingHistory)
        .filter(
            TrackingHistory.order_id == order_id
        )
        .order_by(
            TrackingHistory.timestamp.asc()
        )
        .all()
    )

    return {
        "order_id": order.id,
        "current_status": order.current_status,
        "tracking_history": history
    }