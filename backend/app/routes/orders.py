from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.tracking_service import (
    get_order_tracking,
    add_event,
)
from app.schemas.order import OrderTrackingResponse
from app.database import get_db
from app.models.user import User
from app.routes.auth import get_current_user
from app.schemas.order import (
    OrderCalculateRequest,
    OrderCalculateResponse,
    OrderCreateRequest,
    OrderResponse,
)
from app.services.rate_engine import calculate_rate
from app.models.order import Order
from app.services.order_service import create_order
from pydantic import BaseModel
from app.services.notification_service import create_notification
from app.services.assignment_service import reassign_order
from app.models.notification import Notification

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


class RescheduleRequest(BaseModel):
    reason: str


@router.post(
    "/calculate",
    response_model=OrderCalculateResponse
)
def calculate_order_charge(
    request: OrderCalculateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return calculate_rate(
        pickup_address=request.pickup_address,
        drop_address=request.drop_address,
        length=request.length,
        breadth=request.breadth,
        height=request.height,
        actual_weight=request.actual_weight,
        order_type=request.order_type,
        payment_type=request.payment_type,
        db=db
    )


@router.post(
    "",
    response_model=OrderResponse,
    status_code=201
)
def create_customer_order(
    request: OrderCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "CUSTOMER":
        raise HTTPException(
            status_code=403,
            detail="Only customers can create orders"
        )

    return create_order(
        customer_id=current_user.id,

        actor_id=current_user.id,
        actor_role="CUSTOMER",

        pickup_address=request.pickup_address,
        drop_address=request.drop_address,
        pickup_latitude=request.pickup_latitude,
        pickup_longitude=request.pickup_longitude,
        length=request.length,
        breadth=request.breadth,
        height=request.height,

        actual_weight=request.actual_weight,

        order_type=request.order_type,
        payment_type=request.payment_type,

        db=db
    )


@router.get(
    "/my",
    response_model=list[OrderResponse]
)
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return (
        db.query(Order)
        .filter(
            Order.customer_id == current_user.id
        )
        .order_by(
            Order.created_at.desc()
        )
        .all()
    )


# -----------------------------------------
# Static routes must come before any
# dynamic /{order_id} routes below
# -----------------------------------------

@router.get("/notifications")
def get_my_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return (
        db.query(Notification)
        .filter(
            Notification.recipient_id == current_user.id
        )
        .order_by(
            Notification.id.desc()
        )
        .all()
    )


@router.patch("/notifications/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notification = db.get(
        Notification,
        notification_id
    )

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    if notification.recipient_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot access this notification"
        )

    notification.status = "READ"

    db.commit()
    db.refresh(notification)

    return {
        "message": "Notification marked as read",
        "notification_id": notification.id,
        "status": notification.status
    }


# -----------------------------------------
# Dynamic /{order_id}... routes must come
# AFTER every static route above
# -----------------------------------------

@router.patch(
    "/{order_id}/reschedule",
    response_model=OrderResponse
)
def reschedule_order(
    order_id: int,
    request: RescheduleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # -----------------------------------------
    # 1. Only customer can reschedule
    # -----------------------------------------

    if current_user.role != "CUSTOMER":
        raise HTTPException(
            status_code=403,
            detail="Only customers can reschedule orders"
        )

    # -----------------------------------------
    # 2. Validate reason
    # -----------------------------------------

    reason = request.reason.strip()

    if not reason:
        raise HTTPException(
            status_code=400,
            detail="Reschedule reason is required"
        )

    # -----------------------------------------
    # 3. Get order
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

    # -----------------------------------------
    # 4. Verify ownership
    # -----------------------------------------

    if order.customer_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot reschedule this order"
        )

    # -----------------------------------------
    # 5. Only FAILED orders can be rescheduled
    # -----------------------------------------

    if order.current_status != "FAILED":
        raise HTTPException(
            status_code=400,
            detail="Only FAILED orders can be rescheduled"
        )

    # -----------------------------------------
    # 6. Update status
    # -----------------------------------------

    order.current_status = "RESCHEDULED"

    # -----------------------------------------
    # 7. Tracking event
    # -----------------------------------------

    add_event(
        order_id=order.id,
        status="RESCHEDULED",
        actor_id=current_user.id,
        actor_role="CUSTOMER",
        remarks=reason,
        db=db
    )

    create_notification(
        order_id=order.id,
        recipient_id=order.customer_id,
        channel="EMAIL",
        event_type="DELIVERY_RESCHEDULED",
        db=db
    )

    # -----------------------------------------
    # 8. Save
    # -----------------------------------------

    db.commit()
    db.refresh(order)

    return reassign_order(
        order_id=order.id,
        actor_id=current_user.id,
        actor_role="CUSTOMER",
        db=db
    )


@router.get(
    "/{order_id}/tracking",
    response_model=OrderTrackingResponse
)
def get_customer_order_tracking(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "CUSTOMER":
        raise HTTPException(
            status_code=403,
            detail="Only customers can view order tracking"
        )

    order = db.get(
        Order,
        order_id
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if order.customer_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot view tracking for this order"
        )

    return get_order_tracking(
        order_id=order_id,
        db=db
    )


@router.get(
    "/{order_id}",
    response_model=OrderResponse
)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    order = db.get(
        Order,
        order_id
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if (
        current_user.role == "CUSTOMER"
        and order.customer_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="You cannot access this order"
        )

    return order

@router.patch(
    "/notifications/{notification_id}/read"
)
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.recipient_id == current_user.id
        )
        .first()
    )

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    notification.status = "READ"

    db.commit()
    db.refresh(notification)

    return {
        "message": "Notification marked as read",
        "notification_id": notification.id,
        "status": notification.status
    }