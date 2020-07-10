from lxml import etree
from api import models
from api import process


async def info(*urls):
    cmd = ['svn', 'info', '--xml'] + list(urls)
    result = await process.run_command(*cmd)
    if bool(result['error']) is False:
        xml = etree.fromstring(result['output'])
        result['data'] = [
            models.Info.from_info_entry(entry).dict()
            for entry in xml.xpath('/info/entry')
        ]
    return result


async def proplist(url):
    cmd = ['svn', 'proplist', '--xml', '--verbose', url]
    result = await process.run_command(*cmd)
    if bool(result['error']) is False:
        xml = etree.fromstring(result['output'])
        result['data'] = {
            property.get('name'): property.text
            for property in xml.xpath(f'/properties/target[@path="{url}"]/property')
        }
    return result


async def list_files(url):
    url = url.rstrip('/')
    cmd = ['svn', 'list', '--xml', url]
    result = await process.run_command(*cmd)
    if bool(result['error']) is False:
        xml = etree.fromstring(result['output'])
        result['data'] = [
            models.Info.from_list_entry(entry).dict()
            for entry in xml.xpath(f'/lists/list[@path="{url}"]/entry')
        ]
    return result
