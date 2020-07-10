import os
import re
import tempfile
from lxml import etree
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
                models.Info.from_info(entry).dict()
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
                models.Info.from_list(entry).dict()
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


async def put(url, body=None, message=None):
    message = message or 'PUT ' + re.sub(f"^{os.getenv('ARCHIVE_SERVER')}", "", url)

    if not body:
        # directory
        cmd = ['svn', 'mkdir', '--parents', '--message', message, url]
        result = await process.run_command(*cmd)

    else:
        # file from body
        with tempfile.NamedTemporaryFile() as tf:
            tf.write(body)
            tf.seek(0)
            cmd = ['svnmucc', '--message', message, 'put', tf.name, url]
            result = await process.run_command(*cmd)

    return result
