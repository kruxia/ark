import os
import re
import typing
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


class ProcessOutput(BaseModel):
    output: str
    error: str
    data: dict = None


class Info(BaseModel):
    """
    An item created from a `svn info --xml` entry
    """

    name: str
    kind: str
    rev: int
    date: datetime
    url: str = None
    author: str = None
    size: int = None

    @classmethod
    def from_info(cls, entry):
        """
        Given an lxml.etree info entry element, return a Info object.
        """
        return cls(
            name=entry.get('path'),
            kind=entry.get('kind'),
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
    def from_list(cls, entry):
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


class LogPath(BaseModel):
    name: str
    kind: str
    action: str
    prop_mods: bool
    text_mods: bool

    @classmethod
    def from_path(cls, path):
        return cls(
            name=path.text.lstrip('/'),
            kind=path.get('kind'),
            action=path.get('action'),
            prop_mods=path.get('prop-mods'),
            text_mods=path.get('text-mods'),
        )
    

class LogEntry(BaseModel):
    rev: int
    date: datetime
    message: str
    paths: typing.List[LogPath]

    @classmethod
    def from_logentry(cls, entry):
        return cls(
            rev=entry.get('revision'),
            date=entry.find('date').text,
            message=entry.find('msg').text,
            paths=[
                LogPath.from_path(path)
                for path in 
                entry.xpath('paths/path')
            ]
        )