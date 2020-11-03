import logging
import os
import subprocess
import traceback
import typing

from svn.types import Result

logger = logging.getLogger(__name__)


def run_command(*args, **kwargs):
    """
    Run a subprocess command using asyncio, and return a Result with the stdout and
    stderr as Result.output and Result.error. 
    """
    # Create subprocess
    logger.debug('run_command: %r', args)
    try:
        process = subprocess.Popen(
            args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs
        )
        # Wait for the subprocess to finish
        stdout, stderr = process.communicate()

        # Return stdout, stderr (both str)
        result = Result()
        if stdout:
            result.output = stdout.decode()
        if stderr:
            result.error = stderr.decode()
            result.status = 400

    except Exception as err:
        result = Result(error=str(err), status=500)
        if os.getenv('DEBUG'):
            result.traceback = traceback.format_exc()

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
