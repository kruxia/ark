import json
from datetime import datetime
from pydantic import BaseModel
from uuid import UUID


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (UUID, datetime)):
            return str(obj)
        return super().default(obj)


class Type(BaseModel):
    def dict(self, exclude_none=True, **kwargs):
        """
        By default, exclude None values.
        """
        return super().dict(exclude_none=exclude_none, **kwargs)

    def json(self, exclude_none=True, indent=None, **kwargs):
        return json.dumps(
            self.dict(exclude_none=exclude_none, **kwargs),
            indent=indent,
            cls=JSONEncoder,
        )


class Result(Type):
    """
    Data structure for results, as produced by process.run().

    * `output` = the stdout of the process
    * `error` = the stderr of the process
    * `status` = an HTTP status code for the result
    * `traceback` = the traceback of an exception
    """

    output: str = None
    error: str = None
    status: int = 200
    data: dict = None
    traceback: str = None


class Project(Type):
    # project attributes
    id: UUID = None
    name: str
    created: datetime = None

    # archive attributes
    modified: datetime = None
    size: int = None
    rev: int = None

    class Config:
        orm_mode = True

    def __repr__(self):
        return f"Project(id={self.id!r}, name={self.name!r})"
