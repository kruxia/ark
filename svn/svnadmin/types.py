from pydantic import BaseModel


class Type(BaseModel):
    def dict(self, exclude_none=True, **kwargs):
        """
        By default, exclude None values.
        """
        return super().dict(exclude_none=exclude_none, **kwargs)

    def json(self, exclude_none=True, **kwargs):
        return super().json(exclude_none=exclude_none, **kwargs)


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
