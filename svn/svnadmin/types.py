from pydantic import BaseModel


class Result(BaseModel):
    """
    Data structure for results, as produced by process.run_command().

    * `output` = the stdout of the process
    * `error` = the stderr of the process
    * `status` = an HTTP status code for the result
    * `traceback` = the traceback of an exception
    """

    output: str = ''
    error: str = ''
    status: int = 200
    traceback: str = None
