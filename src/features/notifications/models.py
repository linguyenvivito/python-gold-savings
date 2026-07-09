from datetime import datetime

from pydantic import BaseModel
from pydantic import Field


class ScheduleBroadcastRequest(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    message: str = Field(min_length=1, max_length=2000)
    scheduled_for: datetime


class ScheduleBroadcastResponse(BaseModel):
    id: int
    status: str
    scheduled_for: datetime


class DispatchDueResponse(BaseModel):
    created_notifications: int


class UserNotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    created_at: datetime
    read_at: datetime | None


class MarkAsReadResponse(BaseModel):
    marked_read: bool
