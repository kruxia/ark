import logging
import os
import re
import subprocess
import traceback
import urllib.parse
from svn import process
from svn.types import Result

log = logging.getLogger(__name__)


def create_archive(name):
    """
    Create the archive with the given name, including the template files to configure
    the archive.

    * normalize the name as a path: normalized words separated by hyphens
    * check for existence of this path case-insensitively
    * create the archive at path
    """
    # normalize - words separated by hyphens
    pathname = re.sub(r'\W+', '-', name.strip()).strip('-')
    log.debug(f"{pathname=}")

    # check for existence (case-insensitive for the sake of our weaker brother, Windows)
    path = urllib.parse.unquote(os.getenv('ARCHIVE_FILES'))
    result = process.run_command('ls', path)
    if result.status != 200:
        return result
    else:
        files = result.output.strip()
        if pathname.lower() in re.split(r'\W+', files.lower()):
            return Result(
                status=409, error=f"An archive matching '{name}' already exists."
            )

    # create the archive
    archive_path = path + '/' + pathname
    cmds = [['svnadmin', 'create', archive_path]]

    # copy the current archive template files into the new archive filesystem.
    result = process.run_command('ls', '/var/ark/svn/svntemplate')
    filenames = result.output.strip().split('\n')
    cmds += [
        ['cp', '-R', f'/var/ark/svn/svntemplate/{fn}', archive_path] for fn in filenames
    ]
    cmds += [['chown', '-R', 'apache:apache', archive_path]]

    result = Result(status=201)
    for cmd in cmds:
        cmd_res = process.run_command(*cmd)
        if cmd_res.output:
            result.output = (result.output or '') + cmd_res.output
        if cmd_res.error:
            result.error = (result.error or '') + cmd_res.error

        if result.error:
            result.status = 400
            break

    if result.status == 201:
        result.output = pathname

    return result


def delete_archive(name):
    path = urllib.parse.unquote(os.getenv('ARCHIVE_FILES') + '/' + name)
    if not os.path.isdir(path):
        result = Result(error=f"The archive named '{name}' does not exist.", status=404)
    else:
        result = process.run_command('rm', '-rf', path)
        if result.status == 200:
            result.output = f"The archive named '{name}' was deleted."

    return result
