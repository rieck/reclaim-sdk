from pydantic import Field, field_validator
from datetime import datetime, timezone
from typing import ClassVar, Optional
from enum import Enum
from reclaim_sdk.resources.base import BaseResource


class TaskPriority(str, Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class EventColor(str, Enum):
    NONE = "NONE"
    LAVENDER = "LAVENDER"
    SAGE = "SAGE"
    GRAPE = "GRAPE"
    FLAMINGO = "FLAMINGO"
    BANANA = "BANANA"
    TANGERINE = "TANGERINE"
    PEACOCK = "PEACOCK"
    GRAPHITE = "GRAPHITE"
    BLUEBERRY = "BLUEBERRY"
    BASIL = "BASIL"
    TOMATO = "TOMATO"


class TaskStatus(str, Enum):
    NEW = "NEW"
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"
    CANCELLED = "CANCELLED"
    ARCHIVED = "ARCHIVED"


class EventCategory(str, Enum):
    WORK = "WORK"
    PERSONAL = "PERSONAL"


class Task(BaseResource):
    ENDPOINT: ClassVar[str] = "/api/tasks"

    title: Optional[str] = Field(None, description="Task title")
    notes: Optional[str] = Field(None, description="Task notes")
    event_category: EventCategory = Field(
        default=EventCategory.WORK, alias="eventCategory", description="Event category"
    )
    event_sub_type: Optional[str] = Field(
        None, alias="eventSubType", description="Event subtype"
    )
    time_scheme_id: Optional[str] = Field(
        None, alias="timeSchemeId", description="Time scheme ID (custom hours)"
    )
    time_chunks_required: Optional[int] = Field(
        None, alias="timeChunksRequired", description="Time chunks required"
    )
    min_chunk_size: Optional[int] = Field(
        None, alias="minChunkSize", description="Minimum chunk size"
    )
    max_chunk_size: Optional[int] = Field(
        None, alias="maxChunkSize", description="Maximum chunk size"
    )
    time_chunks_spent: Optional[int] = Field(
        None, alias="timeChunksSpent", description="Time chunks spent"
    )
    time_chunks_remaining: Optional[int] = Field(
        None, alias="timeChunksRemaining", description="Time chunks remaining"
    )
    priority: TaskPriority = Field(None, description="Task priority")
    on_deck: bool = Field(False, alias="onDeck", description="Task is on deck")
    at_risk: bool = Field(False, alias="atRisk", description="Task is at risk")
    deleted: bool = Field(False, alias="deleted", description="Task is deleted")
    adjusted: bool = Field(False, alias="adjusted", description="Task is adjusted")
    deferred: bool = Field(False, alias="deferred", description="Task is deferred")
    always_private: bool = Field(
        False, alias="alwaysPrivate", description="Task is always private"
    )
    status: Optional[TaskStatus] = Field(None, description="Task status")
    due: Optional[datetime] = Field(None, description="Due date")
    created: Optional[datetime] = Field(None, description="Created date")
    updated: Optional[datetime] = Field(None, description="Updated date")
    finished: Optional[datetime] = Field(None, description="Finished date")
    snooze_until: Optional[datetime] = Field(
        None, alias="snoozeUntil", description="Snooze until date"
    )
    index: Optional[float] = Field(None, description="Task index")
    event_color: EventColor = Field(None, alias="eventColor", description="Event color")

    @field_validator(
        "time_chunks_required", "min_chunk_size", "max_chunk_size", mode="before"
    )
    @classmethod
    def validate_chunks(cls, v):
        if v is not None:
            return int(v)
        return v

    @property
    def duration(self) -> Optional[float]:
        return self.time_chunks_required / 4 if self.time_chunks_required else None

    @duration.setter
    def duration(self, hours: float) -> None:
        self.time_chunks_required = int(hours * 4)

    @property
    def min_work_duration(self) -> Optional[float]:
        return self.min_chunk_size / 4 if self.min_chunk_size else None

    @min_work_duration.setter
    def min_work_duration(self, hours: float) -> None:
        self.min_chunk_size = int(hours * 4)

    @property
    def max_work_duration(self) -> Optional[float]:
        return self.max_chunk_size / 4 if self.max_chunk_size else None

    @max_work_duration.setter
    def max_work_duration(self, hours: float) -> None:
        self.max_chunk_size = int(hours * 4)

    @property
    def up_next(self) -> bool:
        return self.on_deck

    @up_next.setter
    def up_next(self, value: bool) -> None:
        self.on_deck = value

    def mark_complete(self) -> None:
        response = self._client.post(f"/api/planner/done/task/{self.id}")
        self.from_api_data(response["taskOrHabit"])

    def mark_incomplete(self) -> None:
        response = self._client.post(f"/api/planner/unarchive/task/{self.id}")
        self.from_api_data(response["taskOrHabit"])

    @classmethod
    def prioritize_by_due(cls) -> None:
        cls._client.patch("/api/tasks/reindex-by-due")

    def prioritize(self) -> None:
        self._client.post(f"/api/planner/prioritize/task/{self.id}")
        self.refresh()

    def add_time(self, hours: float) -> None:
        minutes = int(hours * 60)
        rounded_minutes = round(minutes / 15) * 15
        response = self._client.post(
            f"/api/planner/add-time/task/{self.id}", params={"minutes": rounded_minutes}
        )
        self.from_api_data(response["taskOrHabit"])

    def clear_exceptions(self) -> None:
        response = self._client.post(f"/api/planner/clear-exceptions/task/{self.id}")
        self.from_api_data(response["taskOrHabit"])

    def log_work(self, minutes: int, end: Optional[datetime] = None) -> None:
        params = {"minutes": minutes}
        if end:
            # Convert local time to Zulu time
            end = end.astimezone(timezone.utc)
            # Truncate timestamp to match required format
            params["end"] = end.isoformat(timespec='seconds')[:-6] + ".000Z"

        response = self._client.post(
            f"/api/planner/log-work/task/{self.id}", params=params
        )
        self.from_api_data(response["taskOrHabit"])

    def start(self) -> None:
        response = self._client.post(f"/api/planner/start/task/{self.id}")
        self.from_api_data(response["taskOrHabit"])

    def stop(self) -> None:
        response = self._client.post(f"/api/planner/stop/task/{self.id}")
        self.from_api_data(response["taskOrHabit"])
