import asyncio
import logging
import os
import traceback
import typing

logger = logging.getLogger(__name__)


async def run(*args, **kwargs):
    """
    Run a subprocess command using asyncio, and return a dict with the stdout and stderr
    as `{"output": stdout, "error": stderr}`.
    """
    # Create subprocess
    logger.debug('run: %r', args)
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

    except Exception as exc:
        result = {'output': '', 'error': str(exc)}
        if os.getenv('DEBUG'):
            result['traceback'] = traceback.format_exc()

    logger.debug('--> %r', result)
    return result


def as_user(uid: int, gid: int) -> typing.Callable:
    """
    Used with `run` as the `preexec_fn` key-word argument, in order to run the
    command with the given uid (user id) and gid (group id).
    """

    def fn():
        os.setgid(gid)
        os.setuid(uid)

    return fn
