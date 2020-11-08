import os
import pytest
import requests
import subprocess
from uuid import UUID
from datetime import datetime
from api import svn, ARCHIVE_ADMIN_API
from api.types import Info
from tests.api import ARK_TEST_PREFIX
from tests.api.helpers import cleanup, list_test_archives


# -- TESTS --


def test_ark_get_ok(client):
    """
    GET /ark returns 200 and a list of repositories (here we focus on ARK_TEST_PREFIX)
    """
    cleanup()

    # verify that there are no 'ark_test.*' repositories
    response = client.get('/ark')
    assert response.status_code == 200
    result = response.json()
    print(result)
    test_data = [
        item
        for item in result['data']['archives']
        if item['name'].startswith(ARK_TEST_PREFIX)
    ]
    assert test_data == []

    # create a new archive (backend)
    name = f"{ARK_TEST_PREFIX}01"
    result = requests.post(
        ARCHIVE_ADMIN_API + '/create-archive',
        json={'name': name},
        headers={'Content-Type': 'application/json'},
    )

    # verify that the api now returns a single ARK_TEST_PREFIX entry with expected data
    response = client.get('/ark')
    assert response.status_code == 200
    result = response.json()
    test_data = [
        item
        for item in result['data']['archives']
        if item['name'].startswith(ARK_TEST_PREFIX)
    ]
    assert len(test_data) == 1
    assert test_data[0]['name'] == name
    assert test_data[0]['size'] > 0  # archive sizes are included

    cleanup()


def test_ark_post_ok(client):
    """
    POST /ark with {"name": "..."} creates that archive if it doesn't exist and returns
    201 CREATED
    """
    cleanup()
    name = f"{ARK_TEST_PREFIX}01"
    response = client.post('/ark', json={'name': name})
    print(response.status_code, response.content.decode())
    assert response.status_code == 201
    assert name in [item['name'] for item in list_test_archives()]

    cleanup()


def test_ark_post_exists(client):
    """
    POST /ark with {"name": "..."} returns 409 CONFLICT if it already exists
    """
    cleanup()
    name = f"{ARK_TEST_PREFIX}01"

    # use the ARCHIVE_ADMIN_API to create the archive directly
    create_response = requests.post(
        ARCHIVE_ADMIN_API + '/create-archive',
        json={'name': name},
        headers={'Content-Type': 'application/json'},
    )
    assert create_response.status_code == 201

    # try creating it through the ARK API - should return 409
    response = client.post('/ark', json={'name': name})

    assert response.status_code == 409
    assert name in [item['name'] for item in list_test_archives()]

    cleanup()


def test_ark_post_invalid(client):
    """
    POST /ark without {"name": "..."} returns 400 BAD REQUEST
    """
    cleanup()

    name = f"{ARK_TEST_PREFIX}01"
    response = client.post('/ark', json={'NOT_VALID': name})
    ark_test_repos = list_test_archives()

    assert response.status_code == 400
    assert len(ark_test_repos) == 0

    cleanup()
