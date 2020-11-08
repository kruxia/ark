import logging
import os
import re
import subprocess
import traceback
import urllib.parse
from pathlib import Path
from svnadmin import ARCHIVE_FILES, PACKAGE_PATH, process
from svnadmin.types import Result

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

    # check for existence (case-insensitive for the sake of Windows, our weaker brother)
    path = urllib.parse.unquote(ARCHIVE_FILES)
    result = process.run('ls', path)
    if result.status != 200:
        return result

    files = (result.output or '').strip()
    if pathname.lower() in re.split(r'\W+', files.lower()):
        return Result(status=409, error=f"An archive matching '{name}' already exists.")

    # create the archive and copy the current archive template files into the new
    # archive filesystem. (The template includes conf and hooks, not core repo db files)
    archive_path = path + '/' + pathname
    filenames = (
        process.run('ls', f'{PACKAGE_PATH}/svntemplate').output.strip().split('\n')
    )
    cmds = (
        [['svnadmin', 'create', archive_path]]
        + [
            ['cp', '-R', f'{PACKAGE_PATH}/svntemplate/{fn}', archive_path]
            for fn in filenames
        ]
        + [['chown', '-R', 'apache:apache', archive_path]]
    )
    result = Result(status=201)
    for cmd in cmds:
        cmd_res = process.run(*cmd)
        if cmd_res.output:
            result.output = (result.output or '') + cmd_res.output
        if cmd_res.error:
            result.error = (result.error or '') + cmd_res.error

        if result.error:
            result.status = 409
            break

    if result.status == 201:
        result.data = {'name': pathname}
        du_result = process.run('du', '-sk', archive_path)
        if du_result.status == 200:
            size, name = du_result.output.strip().split('\t')
            result.data['size'] = int(size) * 1024

    return result


def delete_archive(name):
    path = urllib.parse.unquote(ARCHIVE_FILES + '/' + name)
    if not os.path.isdir(path):
        result = Result(error=f"The archive named '{name}' does not exist.", status=404)
    else:
        result = process.run('rm', '-rf', path)
        if result.status == 200:
            result.output = f"The archive named '{name}' was deleted."

    return result


def list_archives():
    # get a list of repositories via ls + du
    result = process.run('ls', ARCHIVE_FILES)
    print(f"ls {ARCHIVE_FILES}: {result=}")
    if result.status != 200:
        return result

    du_results = [
        # -sk returns summary in KB (which we will convert to bytes)
        process.run('du', '-sk', f'{ARCHIVE_FILES}/{name}')
        for name in (result.output or '').strip().split('\n')
        if name
    ]
    if du_results and max([r.status for r in du_results]) > 200:
        return du_results

    data = {
        'archives': [
            {'name': Path(path).name, 'size': int(size) * 1024}
            for size, path in [r.output.strip().split('\t') for r in du_results]
        ]
    }
    return Result(data=data, status=200)
