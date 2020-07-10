from datetime import datetime
from lxml import etree
from pydantic import BaseModel
from uuid import UUID


class Status(BaseModel):
    code: int
    message: str


class HealthStatus(BaseModel):
    files: Status
    archive: Status
    database: Status


class Info(BaseModel):
    name: str
    kind: str
    uuid: UUID
    rev: int
    date: datetime
    author: str = None
    size: int = None

    @classmethod
    def from_entry(cls, entry):
        """
        Given an lxml.etree info entry element, return a Info object.
        """
        return cls(
            name=entry.get('path'),
            kind=entry.get('kind'),
            uuid=next(iter(entry.xpath('repository/uuid/text()'))),
            rev=next(iter(entry.xpath('commit/@revision'))),
            date=next(iter(entry.xpath('commit/date/text()'))),
            author=next(iter(entry.xpath('commit/author/text()')), None),
            size=entry.get('size'),
        )

class ListItem(BaseModel):
    name: str
    kind: str
    rev: int
    date: datetime
    author: str = None
    size: int = None

    @classmethod
    def from_entry(cls, entry):
        """
        Given an lxml.etree list entry element, return a ListItem object.
        """
        return cls(
            name=entry.xpath('name')[0].text,
            kind=entry.get('kind'),
            rev=entry.xpath('commit/@revision')[0],
            date=entry.xpath('commit/date/text()')[0],
            author=next(iter(entry.xpath('commit/author/text()')), None),
            size=next(iter(entry.xpath('size/text()')), None),
        )
