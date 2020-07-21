import asyncio
import logging
import os
import traceback
import typing
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ProcessOutput(BaseModel):
    """
    Data structure for process output, as produced by run_command().

    * `output` = the stdout of the process
    * `error` = the stderr of the process

    TODO: Use this structure for all `run_command` output.
    """

    output: str
    error: str


async def run_command(*args, **kwargs):
    """
    Run a subprocess command using asyncio, and return a dict with the stdout and stderr
    as `{"output": stdout, "error": stderr}`. TODO: Switch to ProcessOutput instead.
    """
    # Create subprocess
    logger.debug('run_command: %r', args)
    try:
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            **kwargs
        )
        # Wait for the subprocess to finish
        stdout, stderr = await process.communicate()

        # Return stdout, stderr (both str)
        result = {'output': stdout.decode(), 'error': stderr.decode()}

    except Exception as err:
        result = {'output': '', 'error': str(err)}
        if os.getenv('DEBUG'):
            result['traceback'] = traceback.format_exc()

    logger.debug('--> %r', result)
    return result


def as_user(uid: int, gid: int) -> typing.Callable:
    """
    Used with `run_command` as the `preexec_fn` key-word argument, in order to run the
    command with the given uid (user id) and gid (group id).
    """

    def fn():
        os.setgid(gid)
        os.setuid(uid)

    return fn
