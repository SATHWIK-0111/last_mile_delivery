from datetime import datetime

from sqlalchemy.orm import Session

from app.models.notification import Notification


def create_notification(
    *,
    order_id: int,
    recipient_id: int,
    channel: str,
    event_type: str,
    db: Session
) -> Notification:
    """
    Create a notification record for an order event.

    The notification starts as PENDING.
    """

    notification = Notification(
        order_id=order_id,
        recipient_id=recipient_id,
        channel=channel.upper(),
        event_type=event_type.upper(),
        status="PENDING",
        sent_at=None
    )

    db.add(notification)

    return notification