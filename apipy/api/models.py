import os
import re
from datetime import datetime
from pydantic import BaseModel

# from uuid import UUID


class Status(BaseModel):
    code: int
    message: str


class HealthStatus(BaseModel):
    files: Status
    archive: Status
    database: Status


class Info(BaseModel):
    """
    An item created from a `svn info --xml` entry
    """

    name: str
    kind: str
    # uuid: UUID
    rev: int
    date: datetime
    url: str = None
    author: str = None
    size: int = None

    @classmethod
    def from_info_entry(cls, entry):
        """
        Given an lxml.etree info entry element, return a Info object.
        """
        return cls(
            name=entry.get('path'),
            kind=entry.get('kind'),
            # uuid=entry.xpath('repository/uuid/text()')[0],
            rev=entry.xpath('commit/@revision')[0],
            date=entry.xpath('commit/date/text()')[0],
            url=re.sub(
                f"^{os.getenv('ARCHIVE_SERVER')}",
                os.getenv('ARCHIVE_URL'),
                entry.xpath('url/text()')[0],
            ),
            author=next(iter(entry.xpath('commit/author/text()')), None),
            size=entry.get('size'),
        )

    @classmethod
    def from_list_entry(cls, entry):
        """
        Given an lxml.etree list entry element, return an Info object.
        """
        return cls(
            name=entry.xpath('name')[0].text,
            kind=entry.get('kind'),
            rev=entry.xpath('commit/@revision')[0],
            date=entry.xpath('commit/date/text()')[0],
            url=re.sub(
                f"^{os.getenv('ARCHIVE_SERVER')}",
                os.getenv('ARCHIVE_URL'),
                '/'.join(
                    [
                        # if the entry is disconnected from its context, URL is relative
                        next(iter(entry.xpath('parent::list/@path')), '.'),
                        entry.xpath('name')[0].text,
                    ]
                ),
            ),
            author=next(iter(entry.xpath('commit/author/text()')), None),
            size=next(iter(entry.xpath('size/text()')), None),
        )
