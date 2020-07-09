from datetime import datetime
from pydantic import BaseModel
from uuid import UUID


class Status(BaseModel):
    code: int
    message: str


class HealthStatus(BaseModel):
    files: Status
    archive: Status
    database: Status


class RepositoryInfo(BaseModel):
    name: str
    uuid: UUID
    rev: int
    date: datetime
    author: str = None

    @classmethod
    def from_entry(cls, entry):
        """
        Given an lxml.etree entry element, return a RepositoryInfo object.
        """
        return cls(
            name=entry.get('path'),
            uuid=next(iter(entry.xpath('repository/uuid/text()')), None),
            rev=int(next(iter(entry.xpath('commit/@revision')), -1)),
            date=next(iter(entry.xpath('commit/date/text()')), None),
            author=next(iter(entry.xpath('commit/author/text()')), None),
        )
