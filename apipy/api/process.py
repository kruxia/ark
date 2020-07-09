import asyncio


async def run_command(*args):
    # Create subprocess
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()
    # Return stdout, stderr (both bytes)
    return {'output': stdout, 'error': stderr}
