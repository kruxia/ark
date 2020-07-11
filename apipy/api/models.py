import os
import re
import typing
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


class ProcessOutput(BaseModel):
    output: str
    error: str
    data: dict = None


# == Info ==


class ArchiveInfo(BaseModel):
    """
    Info about a given archive itself
    """

    root: str
    uuid: UUID

    @classmethod
    def from_info(cls, entry):
        return cls(
            root=re.sub(
                f"^{os.getenv('ARCHIVE_SERVER')}",
                os.getenv('ARCHIVE_URL'),
                entry.find('repository/root').text,
            ),
            uuid=entry.find('repository/uuid').text,
        )


class PathInfo(BaseModel):
    name: str
    kind: str
    url: str = None
    size: int = None

    @classmethod
    def from_info(cls, entry, rev='HEAD'):
        return cls(
            name=entry.get('path'),
            kind=entry.get('kind'),
            url=re.sub(
                f"^{os.getenv('ARCHIVE_SERVER')}",
                os.getenv('ARCHIVE_URL'),
                entry.find('url').text,
            )
            # include the revision (p=peg, r=rev) if not HEAD
            + (f"?p={rev}" if rev and rev != 'HEAD' else ''),
            size=entry.get('size'),
        )

    @classmethod
    def from_list(cls, entry, rev='HEAD'):
        return cls(
            name=entry.find('name').text,
            kind=entry.get('kind'),
            url=re.sub(
                f"^{os.getenv('ARCHIVE_SERVER')}",
                os.getenv('ARCHIVE_URL'),
                '/'.join(
                    [
                        # if the entry is disconnected from its context, URL is relative
                        next(iter(entry.xpath('parent::list/@path')), '.'),
                        entry.find('name').text,
                    ]
                )
                # include the revision (p=peg rev) if not HEAD
                + (f"?p={rev}" if rev and rev != 'HEAD' else ''),
            ),
            size=next(iter(entry.xpath('size/text()')), None),
        )


class VersionInfo(BaseModel):
    rev: int
    date: datetime
    author: str = None

    @classmethod
    def from_info(cls, entry):
        return cls(
            rev=entry.find('commit').get('revision'),
            date=entry.find('commit/date').text,
            author=next(iter(entry.xpath('commit/author/text()')), None),
        )

    from_list = from_info  # same structure


class Info(BaseModel):
    """
    An item created from a `svn info --xml` entry
    """

    path: PathInfo
    version: VersionInfo
    archive: ArchiveInfo = None

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        # 'archive' is only filled from_info(), not from_list()
        if not data['archive']:
            data.pop('archive')
        return data

    @classmethod
    def from_info(cls, entry, rev='HEAD'):
        """
        Given an lxml.etree info entry element, return a Info object.
        """
        return cls(
            archive=ArchiveInfo.from_info(entry),
            path=PathInfo.from_info(entry, rev=rev),
            version=VersionInfo.from_info(entry),
        )

    @classmethod
    def from_list(cls, entry, rev='HEAD'):
        """
        Given an lxml.etree list entry element, return an Info object.
        """
        return cls(
            path=PathInfo.from_list(entry, rev=rev),
            version=VersionInfo.from_list(entry),
        )


# == Log ==


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
            paths=[LogPath.from_path(path) for path in entry.xpath('paths/path')],
        )
