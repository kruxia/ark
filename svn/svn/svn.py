import os
import subprocess
import traceback
import urllib.parse
from svn import process
from svn.types import Result


def create_archive(name):
    """
    Create the archive with the given name, including the template files to configure
    the archive.
    """
    path = urllib.parse.unquote(os.getenv('ARCHIVE_FILES') + '/' + name)
    if os.path.exists(path):
        return Result(status=409, error=f"The archive named '{name}' already exists. ")

    # create the archive
    cmds = [['svnadmin', 'create', path]]

    # copy the current archive template files into the new archive filesystem.
    result = process.run_command('ls', '/var/ark/svn/svntemplate')
    filenames = result.output.strip().split('\n')
    cmds += [['cp', '-R', f'/var/ark/svn/svntemplate/{fn}', path] for fn in filenames]
    cmds += [['chown', '-R', 'apache:apache', path]]

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
