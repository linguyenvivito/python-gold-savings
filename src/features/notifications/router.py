from datetime import datetime, timezone

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import status

from src.core.uow import UnitOfWork
from src.core.uow import get_uow
from src.features.notifications.models import DispatchDueResponse
from src.features.notifications.models import MarkAsReadResponse
from src.features.notifications.models import ScheduleBroadcastRequest
from src.features.notifications.models import ScheduleBroadcastResponse
from src.features.notifications.models import UserNotificationResponse

router = APIRouter(prefix="/notifications", tags=["notifications"])


def _to_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


@router.post(
    "/schedule",
    response_model=ScheduleBroadcastResponse,
    status_code=status.HTTP_201_CREATED,
)
def schedule_broadcast(
    request: ScheduleBroadcastRequest,
    uow: UnitOfWork = Depends(get_uow),
) -> ScheduleBroadcastResponse:
    scheduled_for = _to_utc(request.scheduled_for)

    scheduled = uow.notifications.schedule_broadcast(
        title=request.title.strip(),
        message=request.message.strip(),
        scheduled_for=scheduled_for,
    )

    return ScheduleBroadcastResponse(
        id=scheduled.id,
        status=scheduled.status,
        scheduled_for=scheduled.scheduled_for,
    )


@router.post(
    "/dispatch-due",
    response_model=DispatchDueResponse,
    status_code=status.HTTP_200_OK,
)
def dispatch_due_notifications(
    uow: UnitOfWork = Depends(get_uow),
) -> DispatchDueResponse:
    created_notifications = uow.notifications.dispatch_due(datetime.now(timezone.utc))
    return DispatchDueResponse(created_notifications=created_notifications)


@router.get(
    "/users/{user_id}",
    response_model=list[UserNotificationResponse],
    status_code=status.HTTP_200_OK,
)
def get_user_notifications(
    user_id: int,
    unread_only: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=200),
    uow: UnitOfWork = Depends(get_uow),
) -> list[UserNotificationResponse]:
    notifications = uow.notifications.list_for_user(
        user_id=user_id,
        unread_only=unread_only,
        limit=limit,
    )

    return [
        UserNotificationResponse(
            id=notification.id,
            title=notification.title,
            message=notification.message,
            created_at=notification.created_at,
            read_at=notification.read_at,
        )
        for notification in notifications
    ]


@router.patch(
    "/users/{user_id}/{notification_id}/read",
    response_model=MarkAsReadResponse,
    status_code=status.HTTP_200_OK,
)
def mark_notification_as_read(
    user_id: int,
    notification_id: int,
    uow: UnitOfWork = Depends(get_uow),
) -> MarkAsReadResponse:
    marked_read = uow.notifications.mark_as_read(
        user_id=user_id,
        notification_id=notification_id,
        read_at=datetime.now(timezone.utc),
    )

    if not marked_read:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    return MarkAsReadResponse(marked_read=True)
