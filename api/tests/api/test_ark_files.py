import os
import json
from io import BytesIO
from api.models import Info
from .helpers import cleanup


def setup():
    cleanup()


def teardown():
    cleanup()


def create_archive(client, n):
    """
    Create a new archive. (Use the API to ensure the standard procedure is employed.)
    """
    name = f"{os.getenv('ARK_TEST_PREFIX')}{n:02d}"
    response = client.post('/ark', json={'name': name})
    assert response.status_code == 201
    return name


def create_file(client, name, path, body=b'hello'):
    # PUT the form to the file
    url = f"/ark/{name}/{path}"
    # The body must be posted as a multipart form with "file" for the file data.
    response = client.put(url, files={'file': body})
    return response


# GET /ark/NAME...


def test_get_ark_name_ok(client):
    """
    GET /ark/NAME returns Info, properties, and a list of folders and files.
    """
    name = create_archive(client, 1)

    # with no rev
    response = client.get(f'/ark/{name}')
    data = response.json()
    info = Info(**data['info'])

    assert response.status_code == 200
    assert info.path.name == name
    assert info.path.kind == 'dir'
    assert info.path.url == f"{os.getenv('ARCHIVE_URL')}/{name}"
    assert info.path.size is None
    assert info.version.rev == 0
    assert info.archive.root == info.path.url
    assert data['files'] == []
    assert data['props'] == {}
    assert 'logs' not in data
    assert 'revprops' not in data

    # create a file and rev=1
    create_file(client, name, 'hello.txt')  # rev=1
    logentry = {
        'name': 'hello.txt',
        'kind': 'file',
        'action': 'A',
        'prop_mods': False,
        'text_mods': True,
    }

    # with no rev
    response = client.get(f'/ark/{name}')
    data = response.json()
    info = Info(**data['info'])

    assert response.status_code == 200
    assert info.version.rev == 1
    assert len(data['files']) == 1
    assert data['props'] == {}
    assert 'logs' not in data
    assert 'revprops' not in data

    # with a single rev
    response = client.get(f'/ark/{name}?rev=1')
    data = response.json()
    info = Info(**data['info'])

    assert response.status_code == 200
    assert '?p=1' in info.path.url  # include the rev in the URL for accurate addressing
    assert len(data['files']) == 1
    assert data['props'] == {}
    assert 'svn:date' in data['revprops']
    assert data['log'][0]['rev'] == 1

    for key, val in logentry.items():
        assert data['log'][0]['paths'][0][key] == val

    # with a rev range

    response = client.get(f'/ark/{name}?rev=HEAD:0')
    data = response.json()

    assert response.status_code == 200

    # the only key in the data is 'log'
    assert 'info' not in data
    assert 'props' not in data
    assert 'revprops' not in data
    assert 'files' not in data
    assert data['log'][0]['rev'] == 1
    for key, val in logentry.items():
        if type(val) in [bool, None]:
            assert data['log'][0]['paths'][0][key] is val
        else:
            assert data['log'][0]['paths'][0][key] == val


def test_get_ark_name_404(client):
    """
    GET /ark/NAME on a non-existent archive returns 404
    GET /ark/NAME?rev=N on a non-existent revision N returns 404
    """
    name = create_archive(client, 1)  # hello, {name}
    cleanup()  # goodbye, {name}. it was too short a time to know ya
    response = client.get(f'/ark/{name}')

    assert response.status_code == 404

    name = create_archive(client, 1)  # hello, {name}
    response = client.get(f'/ark/{name}?rev=1')  # non-existent rev

    assert response.status_code == 404


def test_post_ark_name_no_rev_ok(client):
    """
    POST edit [rev]props on archive creates a new rev with those [rev]props
    """
    name = create_archive(client, 1)
    url = f'/ark/{name}'
    data = {'props': {'A': 1}, 'revprops': {'B': 2}}
    response = client.post(url, data=json.dumps(data))
    assert response.status_code == 200

    # Add a property in a new rev=1, and include a revprop with it
    response = client.get(f'{url}?rev=1')
    data = response.json()
    info = Info(**data['info'])

    assert response.status_code == 200
    assert 'p=1' in info.path.url
    assert info.version.rev == 1
    assert data['props']['A'] == '1'  # cast to string
    assert data['revprops']['B'] == '2'
    assert data['log'][0]['paths'][0]['name'] == ''  # root path
    assert data['log'][0]['paths'][0]['kind'] == 'dir'
    assert data['log'][0]['paths'][0]['action'] == 'M'
    assert data['log'][0]['paths'][0]['prop_mods'] is True
    assert data['log'][0]['paths'][0]['text_mods'] is False
    assert data['files'] == []

    # Delete the revprop from rev=1
    data = {"revpropdel": ['B'], "rev": 1}
    response = client.post(url, data=json.dumps(data))

    assert response.status_code == 200

    response = client.get(f"{url}?rev=1")
    data = response.json()
    info = Info(**data['info'])

    assert response.status_code == 200
    assert info.version.rev == 1
    assert data['props']['A'] == '1'
    assert 'B' not in data['revprops']

    # Deleting a non-existent revprop doesn't cause an error
    data = {"revpropdel": ['B'], "rev": 1}
    response = client.post(url, data=json.dumps(data))

    assert response.status_code == 200

    # Delete the property that was set in rev=1 (which creates rev=2)
    data = {"propdel": ['A']}
    response = client.post(url, data=json.dumps(data))

    assert response.status_code == 200

    response = client.get(f"{url}?rev=HEAD")
    data = response.json()
    info = Info(**data['info'])

    assert response.status_code == 200
    assert info.version.rev == 2
    assert 'A' not in data['props']

    # Deleting a non-existent property results in a new revision (even if no change)
    data = {"propdel": ['A']}
    response = client.post(url, data=json.dumps(data))

    assert response.status_code == 200

    response = client.get(f"{url}?rev=HEAD")
    data = response.json()
    info = Info(**data['info'])

    assert response.status_code == 200
    assert info.version.rev == 3


def test_post_ark_name_no_rev_invalid(client):
    """
    When posting to an archive (edit props/revprops) without a revision, the following
    situations return 400 and make no changes:

    * including 'revprops' without 'props'
    * including 'revpropdel' (we're not editing an existing revision)
    """
    name = create_archive(client, 1)
    url = f'/ark/{name}'

    for data in [
        {'props': {'A': 1}, 'revpropdel': ['B']},  # 'revpropdel' not allowed w/o 'rev'
        {'revprops': {'B': 2}},  # 'revprops' not allowed without 'props'
    ]:
        response = client.post(url, data=json.dumps(data))
        assert response.status_code == 400

        response = client.get(url)
        data = response.json()
        assert response.status_code == 200
        assert data['info']['version']['rev'] == 0  # no revisions have been committed


def test_post_ark_name_rev_ok(client):
    """
    POST to archive with a rev (to edit revprops) returns 200 OK

    * revprops and/or revpropdel
    * no props
    * rev is single (no range)
    """
    name = create_archive(client, 1)
    url = f'/ark/{name}'

    # create a starting revision in the archive
    response = client.post(url, data=json.dumps({'props': {'A': 1}}))  # rev=1

    # define post fixtures
    posts = [
        # No action when revprops and revpropdel are empty
        {'revprops': {}, 'rev': 1},
        {'revpropdel': [], 'rev': 1},
        {'revprops': {'A': 2}, 'rev': 1},
        {'revpropdel': ['A'], 'rev': 1},
        # deleting an non-existent revprop is fine
        {'revpropdel': ['A'], 'rev': 1},
        # leave one in place
        {'revprops': {'A': 2}, 'rev': 1},
    ]

    for data in posts:
        response = client.post(url + '?rev=1', data=json.dumps(data))
        assert response.status_code == 200

    # at the end, there should be a single revprop {'A': "1"} on rev 1
    response = client.get(url + '?rev=1')
    data = response.json()
    assert response.status_code == 200
    assert data['revprops']['A'] == '2'  # the last value in the fixtures runs
    assert data['props']['A'] == '1'  # path props maintained separately from revprops


def test_post_ark_name_rev_invalid(client):
    """
    POST to archive with a rev (to edit revprops) returns 400 BAD INPUT

    * rev is range
    * props in data
    """
    name = create_archive(client, 1)
    url = f'/ark/{name}'

    # create a starting revision in the archive
    response = client.post(url, data=json.dumps({'props': {'A': 1}}))  # rev=1

    # define post fixtures
    fixtures = [
        # Cannot include 'props' when editing a revision
        {'revprops': {}, 'rev': "1", 'props': {'A': 0}},
        {'revprops': {'B': 2}, 'rev': "1", 'props': {'A': 0}},
        {'revpropdel': [], 'rev': "1", 'props': {'A': 0}},
        {'revpropdel': ['B'], 'rev': "1", 'props': {'A': 0}},
        # Rev cannot be a range
        {'revprops': {}, 'rev': "1:0"},
        {'revprops': {'C': 3}, 'rev': "1:0"},
        {'revpropdel': [], 'rev': "1:0"},
        {'revpropdel': ['C'], 'rev': "1:0"},
        # Try to leave some in place
        {'revprops': {'B': 2}, 'rev': "1", 'props': {'A': 0}},
        {'revprops': {'C': 3}, 'rev': "1:0"},
    ]

    for fixture in fixtures:
        response = client.post(url + '?rev=1', data=json.dumps(fixture))
        assert response.status_code == 400

    # confirm that there are no changes to props or revprops at rev=1
    response = client.get(url + '?rev=1')
    data = response.json()
    assert response.status_code == 200
    assert 'B' not in data['revprops'] and 'C' not in data['revprops']
    assert data['props']['A'] == '1'  # unchanged despite all attempts to do so


def test_put_ark_name_path(client):
    name = create_archive(client, 1)
    url = f'/ark/{name}'

    fixtures = [
        # directories 201 CREATED
        {'path': 'd1', 'body': b'', 'kind': 'dir', 'status': 201},
        {'path': 'd1/d2', 'body': b'', 'kind': 'dir', 'status': 201},
        {'path': 'd2/d3/d4', 'body': None, 'kind': 'dir', 'status': 201},
        # files 201 CREATED
        {'path': 'hi.txt', 'body': b'hello', 'kind': 'file', 'status': 201},
        {'path': 'd1/hi.txt', 'body': b'hello', 'kind': 'file', 'status': 201},
        {'path': 'd2/d3/d4/hi.txt', 'body': b'hello', 'kind': 'file', 'status': 201},
        # overwrites directory!
        {'path': 'd1', 'body': b'hello', 'kind': 'file', 'status': 201},  # overwrites!
        # directories 409 CONFLICT
        {'path': 'd1', 'body': b'', 'kind': 'file', 'status': 409},  # exists
        {'path': 'd1/d2', 'body': b'', 'kind': None, 'status': 409},  # d1 is file
        {'path': 'd2/d3/d4', 'body': None, 'kind': 'dir', 'status': 409},  # exists
        # files 409 CONFLICT
        {'path': 'd1/d2', 'body': b'hello', 'kind': None, 'status': 409},  # d1 is file
        {'path': 'd5/h1.txt', 'body': b'hello', 'kind': None, 'status': 409},  # no d5
    ]

    for fixture in fixtures:
        print(fixture)
        response = client.put(
            f"{url}/{fixture['path']}",
            files={'file': fixture['body']} if fixture['body'] is not None else None,
        )
        assert response.status_code == fixture['status']
        
        response = client.get(f"{url}/{fixture['path']}")
        data = response.json()
        print(' ', data)
        if fixture['kind'] is None:
            assert response.status_code == 404  # create failed, thing doesn't exist
        else:
            info = Info(**data['info'])
            assert info.path.kind == fixture['kind']


def test_delete_ark_name_path(client):
    name = create_archive(client, 1)
    url = f'/ark/{name}'

    # set up some data in the archive
    for fixture in [
        {'path': 'd1', 'body': None},
        {'path': 'd1/d2', 'body': None},
        {'path': 'hi.txt', 'body': b'hello'},
        {'path': 'd1/hi.txt', 'body': b'hello'},
        {'path': 'd1/d2/hi.txt', 'body': b'hello'},
    ]:
        response = client.put(
            f"{url}/{fixture['path']}",
            data=BytesIO(fixture['body']) if fixture['body'] is not None else None,
        )

    # deletes succeed -- files and folders
    for path in ['hi.txt', 'd1/d2/hi.txt', 'd1']:
        response = client.delete(f"{url}/{path}")
        assert response.status_code == 200
        response = client.get(f"{url}/{path}")
        assert response.status_code == 404

    # deletes fail 404
    for path in ['h1.txt', 'd1/d2/hi.txt', 'd1']:
        response = client.delete(f"{url}/{path}")
        assert response.status_code == 404

    # delete succeeds -- archive itself
    response = client.delete(url)
    assert response.status_code == 200
    response = client.get(url)
    assert response.status_code == 404

    # delete fails -- archive is gone
    response = client.delete(url)
    assert response.status_code == 404
