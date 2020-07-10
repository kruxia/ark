import asyncio
import logging
import os

logger = logging.getLogger(__name__)


async def run_command(*args, **kwargs):
    # Create subprocess
    logger.debug('run_command: %r', args)
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, **kwargs
    )
    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()
    # Return stdout, stderr (both str)
    result = {'output': stdout.decode(), 'error': stderr.decode()}
    logger.debug(result)
    return result


def as_user(uid, gid):
    def fn():
        os.setgid(gid)
        os.setuid(uid)

    return fn
