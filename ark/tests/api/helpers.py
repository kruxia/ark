import json
import os
import subprocess
import requests
from api import svn, ARCHIVE_ADMIN_API
from tests.api import ARK_TEST_PREFIX


def cleanup():
    """
    * remove any existing test archives
    """
    test_archives = list_test_archives()
    for item in test_archives:
        requests.post(
            ARCHIVE_ADMIN_API + '/delete-archive', json={'name': item['name']}
        )


def list_test_archives():
    """
    list any archives that begin with ARK_TEST_PREFIX
    """
    result = requests.get(ARCHIVE_ADMIN_API + '/list-archives')
    return [
        item
        for item in result.json()['data']['archives']
        if item['name'].startswith(ARK_TEST_PREFIX)
    ]
