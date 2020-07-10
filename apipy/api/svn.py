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
        print(result['output'])
        xml = etree.fromstring(result.pop('output').encode())
        result['data'] = {
            property.get('name'): property.text
            for property in xml.xpath(f'/properties/revprops/property')
        }
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
    cmd = ['svn', 'log', '--revision', rev, '--xml', '--verbose', url]
    result = await process.run_command(*cmd)
    if not result['error']:
        print(result['output'])
        xml = etree.fromstring(result.pop('output').encode())
        result['data'] = [
            models.LogEntry.from_logentry(entry).dict()
            for entry in xml.xpath('/log/logentry')
        ]
    return result


