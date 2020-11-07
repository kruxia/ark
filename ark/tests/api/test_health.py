def test_health_ok(client):
    """
    GET /health returns 200 OK
    """
    response = client.get('/health')
    assert response.status_code == 200
    result = response.json()
    for key in ['archive', 'database']:
        assert result['data'][key]['status'] == 200
        assert result['data'][key]['message'] == 'OK'
