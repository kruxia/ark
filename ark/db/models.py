from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel
from uuid import UUID


class Project(BaseModel):
    # project attributes
    id: UUID = None
    name: str
    created: datetime = None

    # archive attributes
    modified: datetime = None
    size: int = None
    rev: int = None

    def __repr__(self):
        return f"Project(id={self.id!r}, name={self.name!r})"
