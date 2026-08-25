from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.schemas.order import OrderTrackingResponse
from app.services.tracking_service import get_order_tracking
from app.database import get_db
from app.models.agent import Agent
from app.models.order import Order
from app.models.user import User
from app.utils.permissions import get_current_user
from app.services.status_service import (
    update_order_status,
    fail_order,
)
from app.services.notification_service import (
    get_user_notifications,
    mark_notification_as_read,
)

router = APIRouter(
    prefix="/agent",
    tags=["Agent"]
)


# ==========================================
# AVAILABILITY
# ==========================================

class AvailabilityUpdate(BaseModel):
    availability_status: str


@router.patch("/availability")
def update_availability(
    request: AvailabilityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "AGENT":
        raise HTTPException(
            status_code=403,
            detail="Only agents can update availability"
        )

    status_value = request.availability_status.upper()

    allowed_statuses = {
        "AVAILABLE",
        "BUSY",
        "OFFLINE"
    }

    if status_value not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=(
                "availability_status must be "
                "AVAILABLE, BUSY or OFFLINE"
            )
        )

    agent = (
        db.query(Agent)
        .filter(Agent.user_id == current_user.id)
        .first()
    )

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent profile not found"
        )

    agent.availability_status = status_value

    db.commit()
    db.refresh(agent)

    return {
        "message": "Availability updated successfully",
        "agent_id": agent.id,
        "availability_status": agent.availability_status
    }


@router.get("/me")
def get_agent_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "AGENT":
        raise HTTPException(
            status_code=403,
            detail="Only agents can access this profile"
        )

    agent = (
        db.query(Agent)
        .filter(Agent.user_id == current_user.id)
        .first()
    )

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent profile not found"
        )

    return {
        "agent_id": agent.id,
        "user_id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "availability_status": agent.availability_status,
        "zone_id": agent.zone_id
    }


# ==========================================
# NOTIFICATIONS
# ==========================================

@router.get("/notifications")
def get_agent_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "AGENT":
        raise HTTPException(
            status_code=403,
            detail="Only agents can access notifications"
        )

    return get_user_notifications(
        recipient_id=current_user.id,
        db=db
    )


@router.patch("/notifications/{notification_id}/read")
def mark_agent_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "AGENT":
        raise HTTPException(
            status_code=403,
            detail="Only agents can update notifications"
        )

    notification = mark_notification_as_read(
        notification_id=notification_id,
        recipient_id=current_user.id,
        db=db
    )

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    return {
        "message": "Notification marked as read",
        "notification_id": notification.id,
        "status": notification.status
    }


@router.get("/orders")
def get_agent_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "AGENT":
        raise HTTPException(
            status_code=403,
            detail="Only agents can view agent orders"
        )

    agent = (
        db.query(Agent)
        .filter(Agent.user_id == current_user.id)
        .first()
    )

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent profile not found"
        )

    return (
        db.query(Order)
        .filter(Order.agent_id == agent.id)
        .order_by(Order.created_at.desc())
        .all()
    )


# ==========================================
# ORDER STATUS
# ==========================================

class OrderStatusUpdate(BaseModel):
    status: str


class FailedDeliveryRequest(BaseModel):
    reason: str


@router.get(
    "/orders/{order_id}/tracking",
    response_model=OrderTrackingResponse
)
def get_agent_order_tracking(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "AGENT":
        raise HTTPException(
            status_code=403,
            detail="Only agents can view order tracking"
        )

    agent = (
        db.query(Agent)
        .filter(Agent.user_id == current_user.id)
        .first()
    )

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent profile not found"
        )

    order = db.get(Order, order_id)

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if order.agent_id != agent.id:
        raise HTTPException(
            status_code=403,
            detail="This order is not assigned to you"
        )

    return get_order_tracking(
        order_id=order_id,
        db=db
    )


@router.patch("/orders/{order_id}/status")
def update_agent_order_status(
    order_id: int,
    request: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # -----------------------------------------
    # 1. Verify user is an agent
    # -----------------------------------------

    if current_user.role != "AGENT":
        raise HTTPException(
            status_code=403,
            detail="Only agents can update order status"
        )

    # -----------------------------------------
    # 2. Get agent profile
    # -----------------------------------------

    agent = (
        db.query(Agent)
        .filter(Agent.user_id == current_user.id)
        .first()
    )

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent profile not found"
        )

    # -----------------------------------------
    # 3. Get order
    # -----------------------------------------

    order = db.get(Order, order_id)

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    # -----------------------------------------
    # 4. Verify agent owns the order
    # -----------------------------------------

    if order.agent_id != agent.id:
        raise HTTPException(
            status_code=403,
            detail="This order is not assigned to you"
        )

    # -----------------------------------------
    # 5. Update status through shared service
    # -----------------------------------------

    return update_order_status(
        order_id=order_id,
        new_status=request.status,
        actor_id=current_user.id,
        actor_role="AGENT",
        db=db
    )


@router.patch("/orders/{order_id}/failed")
def mark_order_failed(
    order_id: int,
    request: FailedDeliveryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # -----------------------------------------
    # 1. Verify agent
    # -----------------------------------------

    if current_user.role != "AGENT":
        raise HTTPException(
            status_code=403,
            detail="Only agents can mark deliveries as failed"
        )

    # -----------------------------------------
    # 2. Find agent profile
    # -----------------------------------------

    agent = (
        db.query(Agent)
        .filter(Agent.user_id == current_user.id)
        .first()
    )

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent profile not found"
        )

    # -----------------------------------------
    # 3. Get order
    # -----------------------------------------

    order = db.get(Order, order_id)

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    # -----------------------------------------
    # 4. Verify assignment
    # -----------------------------------------

    if order.agent_id != agent.id:
        raise HTTPException(
            status_code=403,
            detail="This order is not assigned to you"
        )

    # -----------------------------------------
    # 5. Fail the order
    # -----------------------------------------

    return fail_order(
        order_id=order_id,
        actor_id=current_user.id,
        actor_role="AGENT",
        reason=request.reason,
        db=db
    )