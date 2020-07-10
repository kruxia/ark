import asyncio
import os


async def run_command(*args, **kwargs):
    # Create subprocess
    print(args)
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, **kwargs
    )
    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()
    # Return stdout, stderr (both bytes)
    return {'output': stdout, 'error': stderr}


def as_user(uid, gid):
    def fn():
        os.setgid(gid)
        os.setuid(uid)

    return fn
