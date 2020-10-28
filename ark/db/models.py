from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel
from uuid import UUID


class Project(BaseModel):
    id: UUID = None
    name: str
    description: str = None
    created: datetime = None
    # archive attributes
    modified: datetime = None
    size: int = None
    rev: int = None
    uuid: UUID = None

    def __repr__(self):
        return f"Project(id={self.id!r}, name={self.name!r}, created='{self.created}')"

