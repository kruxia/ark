from pydantic import BaseModel


class Result(BaseModel):
    """
    Data structure for results, as produced by run_command().

    * `output` = the stdout of the process
    * `error` = the stderr of the process

    TODO: Use this structure for all `run_command` output.
    """

    output: str = None
    error: str = None
    status: int = 200
    traceback: str = None
