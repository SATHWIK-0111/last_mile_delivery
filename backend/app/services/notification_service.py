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


def get_user_notifications(
    *,
    recipient_id: int,
    db: Session
):
    """
    Return all notifications belonging to a user.
    """

    return (
        db.query(Notification)
        .filter(
            Notification.recipient_id == recipient_id
        )
        .order_by(
            Notification.id.desc()
        )
        .all()
    )


def mark_notification_as_read(
    *,
    notification_id: int,
    recipient_id: int,
    db: Session
):
    """
    Mark a notification as READ.

    Only the notification owner can mark it as read.
    """

    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.recipient_id == recipient_id
        )
        .first()
    )

    if not notification:
        return None

    notification.status = "READ"

    db.commit()
    db.refresh(notification)

    return notification