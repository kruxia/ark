"""
Interfaces to subversion archives, via both filesystem (svnadmin, svnlook) and HTTP
server (svn, svnmucc).

TODO: When api.process.run_command is updated to return the ProcessOutput data
structure, in cases here where `data` is being added to the structure before return,
instead return the data separately, or None if not created. This will change the
functions' interface and so also require some refactoring in the consumers.
"""

import os
import re
import tempfile
from lxml import etree
from pathlib import Path
from api import models
from api import process


async def info(*urls, rev='HEAD'):
    # `svn info` cannot take a revision range
    if ':' in rev:
        result = {'error': f"Revision range not allowed: rev={rev}"}
    else:
        cmd = ['svn', 'info', '--revision', rev, '--xml'] + list(urls)
        result = await process.run_command(*cmd)
        if not result['error']:
            xml = etree.fromstring(result.pop('output').encode())
            result['data'] = [
                models.Info.from_info(entry, rev=rev).dict()
                for entry in xml.xpath('/info/entry')
            ]
    return result


async def list_files(url, rev='HEAD'):
    # `svn list` cannot take a revision range
    if ':' in rev:
        result = {'error': f'Revision range not allowed: rev={rev}'}
    else:
        cmd = ['svn', 'list', '--revision', rev, '--xml', url]
        result = await process.run_command(*cmd)
        if not result['error']:
            xml = etree.fromstring(result.pop('output').encode())
            result['data'] = [
                models.Info.from_list(entry, rev=rev).dict()
                for entry in xml.xpath(f'/lists/list[@path="{url}"]/entry')
            ]
    return result


async def log(url, rev='HEAD'):
    cmd = ['svn', 'log', '--revision', str(rev), '--xml', '--verbose', url]
    result = await process.run_command(*cmd)
    if not result['error']:
        xml = etree.fromstring(result.pop('output').encode())
        result['data'] = [
            models.LogEntry.from_logentry(entry).dict()
            for entry in xml.xpath('/log/logentry')
        ]
    return result


async def props(url, rev='HEAD'):
    # `svn proplist` cannot take a revision range
    if ':' in rev:
        result = {'error': f'Revision range not allowed: rev={rev}'}
    else:
        cmd = ['svn', 'proplist', '--revision', rev, '--xml', '--verbose', url]
        result = await process.run_command(*cmd)
        if not result['error']:
            xml = etree.fromstring(result.pop('output').encode())
            result['data'] = {
                property.get('name'): property.text
                for property in xml.xpath(f'/properties/target[@path="{url}"]/property')
            }
    return result


async def revprops(url, rev='HEAD'):
    cmd = ['svn', 'proplist', '--revprop', '--revision', rev, '--xml', '--verbose', url]
    result = await process.run_command(*cmd)
    if not result['error']:
        xml = etree.fromstring(result.pop('output').encode())
        result['data'] = {
            property.get('name'): property.text
            for property in xml.xpath('/properties/revprops/property')
        }
    return result


async def propset(url, data):
    """
    Update props and revprops for the url / rev
    * props if no rev (--with-revprop if revprops)
    * revprops if ?rev=M (error if props)
    * error if ?rev=M:N
    """
    rev = str(data.get('rev', ''))
    message = str(data.get('message', ''))

    if ':' in rev:
        result = {'error': f'Cannot set props on a revision range: rev={rev}'}

    elif rev:
        if data.get('props') or data.get('propdel'):
            result = {
                'error': f'Cannot set or delete props on an existing revision: rev={rev}'
            }
        else:
            result = {'error': '', 'output': ''}
            # set revprops on existing revision
            for key, val in data.get('revprops', {}).items():
                cmd = ['svn', 'propset', key, '--revprop', '-r', rev, str(val), url]
                res = await process.run_command(*cmd)
                result['error'] += res['error']
                result['output'] += res['output']

            # del revprops on existing revision
            for key in data.get('revpropdel'):
                cmd = ['svn', 'propdel', key, '--revprop', '-r', rev, url]
                res = await process.run_command(*cmd)
                result['error'] += res['error']
                result['output'] += res['output']

    else:
        if data.get('revpropdel'):
            result = {'error': 'Cannot delete revprops without a revision'}

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
                cmd += ['propset', key, val, url]

            for key in data.get('propdel', []):
                cmd += ['propdel', key, url]

            result = await process.run_command(*cmd)

        elif data.get('revprops'):
            # can't set revprops in the absence of props or an existing revision
            result = {
                'error': (
                    'Cannot set revprops without an existing revision or creating '
                    + 'a propset revision'
                )
            }

        else:
            result = {'error': '', 'output': 'No change'}

    return result


async def put(url, body=None, message=None, revprops=None):
    message = message or 'PUT ' + re.sub(f"^{os.getenv('ARCHIVE_SERVER')}", "", url)

    if not body:
        # directory
        cmd = ['svn', 'mkdir', '--parents', '--message', message]
        for key, val in revprops.items():
            cmd += ['--with-revprop', f"{key}={val}"]

        cmd += [url]
        result = await process.run_command(*cmd)

    else:
        # file from body
        cmd = ['svnmucc', '--message', message]
        for key, val in revprops.items():
            cmd += ['--with-revprop', f"{key}={val}"]

        with tempfile.NamedTemporaryFile() as tf:
            tf.write(body)
            tf.seek(0)
            cmd += ['put', tf.name, url]
            result = await process.run_command(*cmd)

    return result


async def delete_repository(name):
    """
    This is a hard filesystem delete of the entire repository and its history, which
    cannot be undone.
    """
    path = Path(os.getenv('ARCHIVE_FILES')) / name
    if not os.path.exists(path):
        result = {'error': f'Repository not found: {name}'}
    else:
        cmd = ['rm', '-rf', str(path)]
        result = await process.run_command(*cmd)

    return result


async def remove(url, message=None, revprops=None):
    message = message or 'DELETE ' + re.sub(f"^{os.getenv('ARCHIVE_SERVER')}", "", url)
    cmd = ['svn', 'rm', '--message', message]
    for key, val in revprops.items():
        cmd += ['--with-revprop', f"{key}={val}"]
    cmd += [url]
    result = await process.run_command(*cmd)
    result['error'] = re.sub(
        f"'{os.getenv('ARCHIVE_SERVER')}",
        f"'{os.getenv('ARCHIVE_URL')}",
        result['error'],
    )

    return result
