"""
Interfaces to subversion archives, via both filesystem (`svnadmin`, `svnlook`) and HTTP
server (`svn`, `svnmucc`).
"""

import httpx
import json
import logging
import os
import re
import shutil
import tempfile
import traceback
import urllib.parse
import zipfile
from lxml import etree
from pathlib import Path
from api import types
from api import process
from api.types import Result

logger = logging.getLogger(__name__)


async def create_archive(name):
    """
    Create the archive with the given name.
    """
    url = os.getenv('ARCHIVE_ADMIN_API').rstrip('/') + '/create-archive'
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                data=json.dumps({'name': name}),
                headers={'Content-Type': 'application/json'},
            )
            result = Result(**response.json())

    except Exception as exc:
        result = Result(status=500, error=str(exc))
        if os.getenv('DEBUG'):
            result.traceback = traceback.format_exc()

    return result


async def delete_archive(name):
    """
    Delete the named archive from the archive filesystem. (This is a hard filesystem
    delete of the entire archive and its history, which cannot be undone.)
    """
    url = os.getenv('ARCHIVE_ADMIN_API').rstrip('/') + '/delete-archive'
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                data=json.dumps({'name': name}),
                headers={'Content-Type': 'application/json'},
            )
            result = Result(**response.json())

    except Exception as exc:
        result = Result(status=500, error=str(exc))
        if os.getenv('DEBUG'):
            result.traceback = traceback.format_exc()

    return result


async def list_archives():
    url = os.getenv('ARCHIVE_ADMIN_API').rstrip('/') + '/list-archives'
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url, headers={'Content-Type': 'application/json'},
            )
            result = Result(**response.json())

    except Exception as exc:
        result = Result(status=500, error=str(exc))
        if os.getenv('DEBUG'):
            result.traceback = traceback.format_exc()

    return result


async def info(*urls, rev='HEAD'):
    """
    Return a list of Info data on the given url(s) and revision.
    """
    # `svn info` cannot take a revision range
    if ':' in rev:
        result = Result(error=f"Revision range not allowed: rev={rev}", status=400)
    else:
        if rev != 'HEAD':
            # add `@{rev}` to each url to get the info at that rev.
            urls = [url + f'@{rev}' for url in urls]
        result = await process.run('svn', 'info', '--xml', *urls)
        logger.debug(f"{result=}")
        if not result.error:
            xml = etree.fromstring(result.output.encode())
            result.data = {
                'entries': [
                    types.Info.from_info(entry, rev=rev).dict()
                    for entry in xml.xpath('/info/entry')
                ]
            }
        elif (
            'Could not find the requested SVN filesystem' in result.error
            or 'No such revision' in result.error
        ):
            result.status = 404

    return result


async def ls(*urls, rev='HEAD'):
    """
    Return a list of files at the given url and revision as Info data. The url must be a
    directory.
    """
    # `svn ls` cannot take a revision range
    if ':' in rev:
        result = Result(error=f'Revision range not allowed: rev={rev}', status=400)
    else:
        cmd = ['svn', 'ls', '--xml']
        for url in urls:
            if rev != 'HEAD':
                url = f'{url}@{rev}'
            cmd.append(urllib.parse.unquote_plus(url))

        result = await process.run(*cmd)
        if not result.error:
            xml = etree.fromstring(result.output.encode())
            result.data = {
                'files': [
                    types.Info.from_ls(entry, rev=rev).dict()
                    for entry in xml.xpath('/lists/list/entry')
                ]
            }

    return result


async def export(url, rev='HEAD'):
    """
    Export the content of the given URL. If it's a folder, zip it. Return result dict.
    """
    if ':' in rev:
        result = Result(error=f'Revision range not allowed: rev={rev}', status=400)
    else:
        if rev != 'HEAD':
            rev_url = f'{url}@{rev}'
        else:
            rev_url = url

        with tempfile.TemporaryDirectory() as tempdir:
            filepath = os.path.join(
                tempdir, urllib.parse.unquote_plus(url.split('/')[-1])
            )

            cmd = ['svn', 'export', urllib.parse.unquote_plus(rev_url), filepath]
            result = await process.run(*cmd)

            if not result.error:
                if os.path.isfile(filepath):
                    srcpath = filepath
                else:
                    # directory -- zip it
                    srcpath = filepath + '.zip'
                    with zipfile.ZipFile(srcpath, 'w', zipfile.ZIP_DEFLATED) as zf:
                        for root, dirs, files in os.walk(filepath):
                            for directory in dirs:
                                filename = os.path.join(root, directory)
                                arcname = os.path.relpath(filename, tempdir)
                                zf.write(filename, arcname)
                            for file in files:
                                filename = os.path.join(root, file)
                                arcname = os.path.relpath(filename, tempdir)
                                zf.write(filename, arcname)

                outpath = '/var/tmp/' + os.path.split(tempdir)[-1]
                os.makedirs(outpath)

                if rev == 'HEAD':
                    filename = os.path.split(srcpath)[-1]
                else:
                    fp, ext = os.path.splitext(srcpath)
                    basename = os.path.basename(fp)
                    filename = f"{basename}@{rev}{ext}"

                result.data = {'filepath': f"{outpath}/{filename}"}
                shutil.copy(srcpath, result.data['filepath'])

    return result


async def log(url, rev='HEAD'):
    """
    Return a list of LogEntry data on the given url and revision (single or range).
    """
    if rev != 'HEAD':
        url += f"@{rev.split(':')[0]}"
    cmd = [
        'svn',
        'log',
        '--revision',
        str(rev),
        '--xml',
        '--verbose',
        urllib.parse.unquote_plus(url),
    ]

    result = await process.run(*cmd)
    if not result.error:
        xml = etree.fromstring(result.output.encode())
        result.data = {
            'entries': [
                types.LogEntry.from_logentry(entry).dict()
                for entry in xml.xpath('/log/logentry')
            ]
        }

    return result


async def props(url, rev='HEAD'):
    """
    Return a dict with the props data on the given url and revision.
    """
    # `svn proplist` cannot take a revision range
    if ':' in rev:
        result = Result(error=f'Revision range not allowed: rev={rev}', status=400)
    else:
        if rev != 'HEAD':
            rev_url = f"{url}@{rev}"
        else:
            rev_url = url
        cmd = [
            'svn',
            'proplist',
            '--xml',
            '--verbose',
            urllib.parse.unquote_plus(rev_url),
        ]

        result = await process.run(*cmd)
        if not result.error:
            xml = etree.fromstring(result.output.encode())
            result.data = {
                property.get('name'): property.text
                # target@path is given with trailing slash stripped, so normalize to cp.
                for property in xml.xpath(
                    f'/properties/target[@path="{url.rstrip("/")}"]/property'
                )
            }
        elif (
            'Could not find the requested SVN filesystem' in result.error
            or 'No such revision' in result.error
            or 'Unknown node kind' in result.error
        ):
            result.status = 404

    return result


async def revprops(url, rev='HEAD'):
    """
    Return a dict with the revprops data on the given url and rev.
    """
    cmd = [
        'svn',
        'proplist',
        '--revprop',
        '--revision',
        rev,
        '--xml',
        '--verbose',
        urllib.parse.unquote_plus(url),
    ]

    result = await process.run(*cmd)
    if not result.error:
        xml = etree.fromstring(result.output.encode())
        result.data = {
            property.get('name'): property.text
            for property in xml.xpath('/properties/revprops/property')
        }

    return result


async def propset(url, data):
    """
    Update props and revprops with the given url and data. Return a dict with the
    combined `output` and `error` from the commands run on the data.

    * If data['rev'] is given, edit revprops in an existing revision.

      * data['rev'] must not be a range (no ':' allowed)
      * data['props'] and data['propdel'] must not be present (cannot set or delete
        props on an existing revision)
      * data['revprops'] is a dict with revprops to set on the revision. For each
        revprop, call `svn propset --revprop`
      * data['revpropdel'] is a list with revprop keys to delete. For each key, call
        `svn propdel --revprop`

    * If data['rev'] is not given, call `svn mucc` to create a new revision with the
      given props and revprops.

      * data['props'] is a dict with props to set. For each prop, add a `propset`
        command to the `svn mucc` call
      * data['propdel'] is a list with prop keys to delete. For each key, add a
        `propdel` command to the `svn mucc` call
      * data['revprops'] is a dict with revprops to set on the revision. For each
        revprop key and value, add `--with-revprop key=value` to the `svn mucc` call
      * data['revpropdel'] must not be present (cannot delete revprops on a new
        revision)
    """
    rev = str(data.get('rev', ''))
    message = str(data.get('message', ''))

    if ':' in rev:
        result = Result(
            error=f'Cannot set props on a revision range: rev={rev}', status=400
        )

    elif rev:
        if data.get('props') or data.get('propdel'):
            result = Result(
                error=f'Cannot set or delete props on an existing revision: rev={rev}',
                status=400,
            )
        else:
            result = Result(output='', error='')
            # set revprops on existing revision
            for key, val in data.get('revprops', {}).items():
                cmd = [
                    'svn',
                    'propset',
                    key,
                    '--revprop',
                    '-r',
                    rev,
                    str(val),
                    urllib.parse.unquote_plus(url),
                ]

                res = await process.run(*cmd)
                result.error += res.error
                result.output += res.output

            # del revprops on existing revision
            for key in data.get('revpropdel', []):
                cmd = [
                    'svn',
                    'propdel',
                    key,
                    '--revprop',
                    '-r',
                    rev,
                    urllib.parse.unquote_plus(url),
                ]

                res = await process.run(*cmd)
                result.error += res.error
                result.output += res.output

    else:
        if data.get('revpropdel'):
            result = Result(
                error='Cannot delete revprops without a revision', status=400
            )

        elif data.get('props') or data.get('propdel'):
            if data.get('props'):
                message += (
                    "\npropset keys=['" + "', '".join(data['props'].keys()) + "']"
                )
            if data.get('propdel'):
                message += "\npropdel keys=['" + "', '".join(data['propdel']) + "']"

            # set/del props with new revision, optionally with revprops as well
            cmd = ['svnmucc', '-m', message.strip()]

            for key, val in data.get('revprops', {}).items():
                cmd += ['--with-revprop', f'{key}={val}']

            for key, val in data.get('props', {}).items():
                cmd += ['propset', key, str(val), urllib.parse.unquote_plus(url)]

            for key in data.get('propdel', []):
                cmd += ['propdel', key, urllib.parse.unquote_plus(url)]

            result = await process.run(*cmd)

        elif data.get('revprops'):
            # can't set revprops in the absence of editing/deleting props in a revision
            result = Result(
                error=(
                    'Cannot set revprops without an existing revision or creating '
                    + 'a revision to set/delete props'
                ),
                status=400,
            )

        else:
            result = Result(output='No change')

    return result


async def put(url, body=None, message=None, revprops=None):
    """
    Create or update a file or directory at the given url with the given body (if any),
    message (if any), and revprops (if any) for the new revision. Return a process
    result object containing `output` and `error` (if any) from the process.

    TODO: Allow setting props on the URL at the same time.

    Rules:

    * If body is given (not None or empty), we assume that a file is intended.
      * If the file doesn't exist, it will be created.
      * If the file exists, it will be updated.
      * If the given url is currently a folder, it and all its content will be
        overwritten by the new file. (TODO? Check for the existence of an existing
        folder and prevent this behavior?)
      * If the parent directory of the file doesn't exist, an error will be returned and
        the file will not be created. (TODO? Check for the existence of the parent
        folder and create it if it doesn't exist?)

    * If body is None or empty, we assume that a directory is intended.
      * If the directory doesn't exist, it will be created, along with all parents.
      * If the directory already exists, an error is returned (updating is meaningless).

    (NOTE: These rules closely mirror the default behaviors of the `svn` and `svn mucc`
    commands. Making the TODO? adjustments would require querying the archive before the
    put operations.)
    """
    message = message or 'PUT ' + re.sub(f"^{os.getenv('ARCHIVE_SERVER')}", "", url)

    if not body:
        # directory
        cmd = ['svn', 'mkdir', '--parents', '--message', message]
        for key, val in revprops.items():
            cmd += ['--with-revprop', f"{key}={val}"]

        cmd += [urllib.parse.unquote_plus(url)]

        result = await process.run(*cmd)

    else:
        # file from body
        cmd = ['svnmucc', '--message', message]
        for key, val in (revprops or {}).items():
            cmd += ['--with-revprop', f"{key}={val}"]

        with tempfile.NamedTemporaryFile() as tf:
            tf.write(body)
            tf.seek(0)
            cmd += ['put', tf.name, urllib.parse.unquote_plus(url)]

            result = await process.run(*cmd)

    result.status = 409 if result.error else 201
    print(result.dict())
    return result


async def remove(url, message=None, revprops=None):
    """
    Remove the given `url` and all its children (if a directory). Set the given
    `message` and `revprops` on the new revision.
    """
    message = message or 'DELETE ' + re.sub(f"^{os.getenv('ARCHIVE_SERVER')}", "", url)
    cmd = ['svn', 'rm', '--message', message]
    for key, val in revprops.items():
        cmd += ['--with-revprop', f"{key}={val}"]
    cmd += [urllib.parse.unquote_plus(url)]

    result = await process.run(*cmd)
    result.error = re.sub(
        f"'{os.getenv('ARCHIVE_SERVER')}", f"'{os.getenv('ARCHIVE_URL')}", result.error,
    )
    if result.error:
        result.status = 404

    return result
