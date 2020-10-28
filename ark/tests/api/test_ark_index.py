import os
import subprocess
from uuid import UUID
from datetime import datetime
from api.models import Info
from .helpers import cleanup, list_ark_test_archives


# -- TESTS --


def test_ark_get_ok(client):
    """
    GET /ark returns 200 and a list of repositories (here we focus on
    os.getenv('ARK_TEST_PREFIX'))
    """
    cleanup()

    # verify that there are no 'ark_test.*' repositories
    response = client.get('/ark')
    test_data = [
        entry
        for entry in response.json()['files']
        if entry.get('path').get('name').startswith(os.getenv('ARK_TEST_PREFIX'))
    ]
    assert response.status_code == 200
    assert test_data == []

    # create a new archive (backend)
    path = f"{os.getenv('ARCHIVE_FILES')}/{os.getenv('ARK_TEST_PREFIX')}01"
    subprocess.check_output(['svnadmin', 'create', path])

    # verify that the api now returns a single os.getenv('ARK_TEST_PREFIX') entry with
    # expected data
    response = client.get('/ark')
    test_data = [
        entry
        for entry in response.json()['files']
        if entry.get('path').get('name').startswith(os.getenv('ARK_TEST_PREFIX'))
    ]
    assert response.status_code == 200
    assert len(test_data) == 1
    repo_info = Info(**test_data[0])
    assert repo_info.path.name == f"{os.getenv('ARK_TEST_PREFIX')}01"
    assert repo_info.version.rev == 0
    assert isinstance(repo_info.version.date, datetime)
    assert isinstance(repo_info.archive.uuid, UUID)
    assert repo_info.path.size > 0  # archive sizes are included

    cleanup()


def test_ark_post_ok(client):
    """
    POST /ark with {"name": "..."} creates that archive if it doesn't exist and returns
    201 CREATED
    """
    cleanup()
    name = f"{os.getenv('ARK_TEST_PREFIX')}01"
    path = f"{os.getenv('ARCHIVE_FILES')}/{name}"
    response = client.post('/ark', json={'name': name})
    ark_test_repos = list_ark_test_archives()

    assert response.status_code == 201
    assert path in ark_test_repos

    cleanup()


def test_ark_post_exists(client):
    """
    POST /ark with {"name": "..."} returns 409 CONFLICT if it already exists
    """
    cleanup()
    name = f"{os.getenv('ARK_TEST_PREFIX')}01"
    path = f"{os.getenv('ARCHIVE_FILES')}/{name}"
    subprocess.check_output(
        ['svnadmin', 'create', f"{os.getenv('ARCHIVE_FILES')}/{name}"]
    )
    response = client.post('/ark', json={'name': name})
    ark_test_repos = list_ark_test_archives()

    assert response.status_code == 409
    assert path in ark_test_repos

    cleanup()


def test_ark_post_invalid(client):
    """
    POST /ark without {"name": "..."} returns 400 BAD REQUEST
    """
    cleanup()

    name = f"{os.getenv('ARK_TEST_PREFIX')}01"
    response = client.post('/ark', json={'NOT_VALID': name})
    ark_test_repos = list_ark_test_archives()

    assert response.status_code == 400
    assert len(ark_test_repos) == 0

    cleanup()
