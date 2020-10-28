def test_health_ok(client):
    """
    GET /health returns 200 OK
    """
    response = client.get('/health')
    assert response.status_code == 200
    data = response.json()
    for key in [
        'files',
        'archive',
        # 'database'
    ]:
        assert data[key]['code'] == 200
        assert data[key]['message'] == 'OK'
