import os
import subprocess
from uuid import UUID
from datetime import datetime
from api.models import Info

ARK_TEST_PREFIX = '__ARK_TEST.'

# -- HELPERS --


def setup():
    cleanup()


def teardown():
    cleanup()


def cleanup():
    # remove any repositories that begin with ARK_TEST_PREFIX
    ark_test_repos = list_ark_test_repos()
    if len(ark_test_repos) > 0:
        subprocess.check_output(['rm', '-rf'] + ark_test_repos)


def list_ark_test_repos():

    return [
        f"{os.getenv('ARCHIVE_FILES')}/{name}"
        for name in subprocess.check_output(['ls', f"{os.getenv('ARCHIVE_FILES')}"])
        .decode()
        .strip()
        .split()
        if name.startswith(ARK_TEST_PREFIX)
    ]


# -- TESTS --


def test_ark_get_ok(client):
    """
    GET /ark returns 200 and a list of repositories (here we focus on ARK_TEST_PREFIX)
    """
    setup()

    # verify that there are no 'ark_test.*' repositories
    response = client.get('/ark')
    test_data = [
        entry
        for entry in response.json()
        if entry.get('path').get('name').startswith(ARK_TEST_PREFIX)
    ]
    assert response.status_code == 200
    assert test_data == []

    # create a new repository (backend)
    subprocess.check_output(
        ['svnadmin', 'create', f"{os.getenv('ARCHIVE_FILES')}/{ARK_TEST_PREFIX}01"]
    )

    # verify that the api now returns a single ARK_TEST_PREFIX entry with expected data
    response = client.get('/ark')
    test_data = [
        entry
        for entry in response.json()
        if entry.get('path').get('name').startswith(ARK_TEST_PREFIX)
    ]
    assert response.status_code == 200
    assert len(test_data) == 1
    repo_info = Info(**test_data[0])
    assert repo_info.path.name == f'{ARK_TEST_PREFIX}01'
    assert repo_info.version.rev == 0
    assert isinstance(repo_info.version.date, datetime)
    assert isinstance(repo_info.archive.uuid, UUID)

    teardown()


def test_ark_post_ok(client):
    """
    POST /ark with {"name": "..."} creates that repository if it doesn't exist and
    returns 201 CREATED
    """
    setup()
    name = f"{ARK_TEST_PREFIX}01"
    path = f"{os.getenv('ARCHIVE_FILES')}/{name}"
    response = client.post('/ark', json={'name': name})
    ark_test_repos = list_ark_test_repos()

    assert response.status_code == 201
    assert path in ark_test_repos

    teardown()


def test_ark_post_exists(client):
    """
    POST /ark with {"name": "..."} returns 409 CONFLICT if it already exists
    """
    setup()
    name = f"{ARK_TEST_PREFIX}01"
    path = f"{os.getenv('ARCHIVE_FILES')}/{name}"
    subprocess.check_output(
        ['svnadmin', 'create', f"{os.getenv('ARCHIVE_FILES')}/{name}"]
    )
    response = client.post('/ark', json={'name': name})
    ark_test_repos = list_ark_test_repos()

    assert response.status_code == 409
    assert path in ark_test_repos

    teardown()


def test_ark_post_invalid(client):
    """
    POST /ark without {"name": "..."} returns 400 BAD REQUEST
    """
    setup()

    name = f"{ARK_TEST_PREFIX}01"
    response = client.post('/ark', json={'NOT_VALID': name})
    ark_test_repos = list_ark_test_repos()

    assert response.status_code == 400
    assert len(ark_test_repos) == 0

    teardown()
