import os
import re
import typing
from datetime import datetime
from enum import Enum
from pydantic import BaseModel
from uuid import UUID


class Status(BaseModel):
    """
    The base HTTP status response object for our API.
    """

    code: int
    message: str


# == SVN Info ==


class NodeKind(Enum):
    File = 'file'
    Dir = 'dir'


class ArchiveInfo(BaseModel):
    """
    Data about an archive itself, as provided by `svn info`.
    """

    name: str
    root: str
    uuid: UUID

    @classmethod
    def from_info(cls, entry):
        """
        Given a `svn info` entry element, return ArchiveInfo.
        """
        root = re.sub(
            f"^{os.getenv('ARCHIVE_SERVER')}",
            os.getenv('ARCHIVE_URL'),
            entry.find('repository/root').text,
        )
        name = root.split('/')[-1]
        return cls(name=name, root=root, uuid=entry.find('repository/uuid').text,)


class PathInfo(BaseModel):
    """
    Data about a path in an archive, as provided by either `svn info` or `svn list`.
    """

    name: str
    kind: NodeKind
    url: str = None
    size: int = None

    @classmethod
    def from_info(cls, entry, rev='HEAD'):
        """
        Given a `svn info` entry element, return PathInfo. Include the rev in the url if
        the rev is not HEAD (to make the URL an accurate link to THIS rev of target.)
        """
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
        """
        Given a `svn list` entry element, return PathInfo. Include the rev in the url if
        the rev is not HEAD (to make the URL an accurate link to THIS rev of target.)
        """
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
    """
    Data about a version in an archive, as provided by either `svn info` or `svn list`.
    """

    rev: int
    date: datetime
    author: str = None

    @classmethod
    def from_info(cls, entry):
        """
        Given a `svn info` entry element, return VersionInfo.
        """
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
        Given a `svn info` entry element, return Info.
        """
        return cls(
            archive=ArchiveInfo.from_info(entry),
            path=PathInfo.from_info(entry, rev=rev),
            version=VersionInfo.from_info(entry),
        )

    @classmethod
    def from_list(cls, entry, rev='HEAD'):
        """
        Given a `svn list` entry element, return Info.
        """
        return cls(
            path=PathInfo.from_list(entry, rev=rev),
            version=VersionInfo.from_list(entry),
        )


# == SVN Log ==


class LogPathAction(Enum):
    Added = 'A'
    Deleted = 'D'
    Modified = 'M'
    Replaced = 'R'


class LogPath(BaseModel):
    """
    Data structure for an archive file path, as returned by `svn log`.
    """

    name: str
    kind: NodeKind
    action: LogPathAction
    prop_mods: bool
    text_mods: bool

    @classmethod
    def from_path(cls, path):
        """
        Given a `svn log` path element, return LogPath.
        """
        return cls(
            name=path.text.lstrip('/'),
            kind=path.get('kind'),
            action=LogPathAction(path.get('action')),
            prop_mods=path.get('prop-mods'),
            text_mods=path.get('text-mods'),
        )


class LogEntry(BaseModel):
    """
    Data structure for an archive log entry, as returned by `svn log`.
    """

    rev: int
    date: datetime
    message: str = None
    paths: typing.List[LogPath]

    @classmethod
    def from_logentry(cls, entry):
        """
        Given a `svn log` logentry element, return LogEntry.
        """
        return cls(
            rev=entry.get('revision'),
            date=entry.find('date').text,
            message=entry.find('msg').text,
            paths=[LogPath.from_path(path) for path in entry.xpath('paths/path')],
        )
