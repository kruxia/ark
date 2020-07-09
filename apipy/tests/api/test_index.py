def test_index_ok(client):
    """
    GET / returns 200 OK
    """
    response = client.get('/')
    assert response.status_code == 200
