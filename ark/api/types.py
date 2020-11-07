import os
import re
import typing
import urllib.parse
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, root_validator, validator
from uuid import UUID


class Type(BaseModel):
    def dict(self, exclude_none=True, **kwargs):
        """
        by default, exclude None values.
        """
        return super().dict(exclude_none=exclude_none, **kwargs)

    def json(self, exclude_none=True, **kwargs):
        return super().json(exclude_none=exclude_none, **kwargs)


class Result(Type):
    """
    The base result object for our API. Used for both HTTP response data and for process
    results.
    """

    status: int = 200
    message: str = None
    output: str = None
    error: str = None
    data: dict = None
    traceback: str = None


class HealthStatus(Type):
    """
    Data structure for the /health response.
    """

    archive: Result
    database: Result


# == SVN Info ==


class NodeKind(Enum):
    File = 'file'
    Dir = 'dir'


class URL(Type):
    scheme: str
    netloc: str
    path: str
    params: str
    query: str
    fragment: str

    def __str__(self):
        urlist = [f"{self.scheme}://{self.netloc}{self.path}"]
        if self.params:
            urlist.append(f';{self.params}')
        if self.query:
            urlist.append(f'?{self.query}')
        if self.fragment:
            urlist.append(f'#{self.fragment}')
        return ''.join(urlist)

    @classmethod
    def from_string(cls, url):
        pr = urllib.parse.urlparse(url)
        return cls(
            scheme=pr.scheme,
            netloc=pr.netloc,
            path=pr.path,
            params=pr.params,
            query=pr.query,
            fragment=pr.fragment,
        )


class ArchiveInfo(Type):
    """
    Data about an archive itself, as provided by `svn info`.
    """

    name: str
    root: str

    @validator('root')
    def convert_root(cls, value):
        """
        Ensure archive root path has trailing slash
        """
        url = URL.from_string(str(value))
        url.path = url.path.rstrip('/') + '/'
        return str(url)

    @validator('name')
    def convert_name(cls, value):
        return urllib.parse.unquote(value)

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
        name = root.rstrip('/').split('/')[-1]
        return cls(name=name, root=root)


class PathInfo(Type):
    """
    Data about a path in an archive, as provided by either `svn info` or `svn ls`.
    """

    name: str
    kind: NodeKind
    url: str = None
    size: int = None

    @root_validator
    def normalize_values(cls, values):
        """
        + Unquote instance.name
        + Ensure that instance.url has a trailing slash if it's a 'dir'.
        """
        values['name'] = urllib.parse.unquote(values['name'])
        if 'url' in values and values['url'] is not None:
            url = URL.from_string(str(values['url']))
            if values['kind'] == NodeKind.Dir:
                url.path = url.path.rstrip('/') + '/'
            values['url'] = str(url)
        return values

    @classmethod
    def from_info(cls, entry, rev='HEAD'):
        """
        Given a `svn info` entry element, return PathInfo. Include the rev in the url if
        the rev is not HEAD (to make the URL an accurate link to THIS rev of target.)
        """
        url = (
            re.sub(
                f"^{os.getenv('ARCHIVE_SERVER')}",
                os.getenv('ARCHIVE_URL'),
                entry.find('url').text,
            )
            # include the revision (p=peg, r=rev) if not HEAD
            + (f"?p={rev}" if rev and rev != 'HEAD' else '')
        )
        return cls(
            name=entry.get('path'),
            kind=entry.get('kind'),
            url=url,
            size=entry.get('size'),
        )

    @classmethod
    def from_ls(cls, entry, rev='HEAD'):
        """
        Given a `svn ls` entry element, return PathInfo. Include the rev in the url if
        the rev is not HEAD (to make the URL an accurate link to THIS rev of target.)
        """
        url = re.sub(
            f"^{os.getenv('ARCHIVE_SERVER')}",
            os.getenv('ARCHIVE_URL'),
            '/'.join(
                [
                    # if the entry is disconnected from its context, URL is relative
                    next(iter(entry.xpath('parent::list/@path')), '.'),
                    urllib.parse.quote(entry.find('name').text),
                ]
            )
            # include the revision (p=peg rev) if not HEAD
            + (f"?p={rev}" if rev and rev != 'HEAD' else ''),
        )
        return cls(
            name=entry.find('name').text,
            kind=entry.get('kind'),
            url=url,
            size=next(iter(entry.xpath('size/text()')), None),
        )


class VersionInfo(Type):
    """
    Data about a version in an archive, as provided by either `svn info` or `svn ls`.
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

    from_ls = from_info  # same structure


class Info(Type):
    """
    An item created from a `svn info --xml` entry
    """

    path: PathInfo
    version: VersionInfo
    archive: ArchiveInfo = None

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
    def from_ls(cls, entry, rev='HEAD'):
        """
        Given a `svn ls` entry element, return Info.
        """
        return cls(
            path=PathInfo.from_ls(entry, rev=rev), version=VersionInfo.from_ls(entry),
        )


# == SVN Log ==


class LogPathAction(Enum):
    Added = 'A'
    Deleted = 'D'
    Modified = 'M'
    Replaced = 'R'


class LogPath(Type):
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


class LogEntry(Type):
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
