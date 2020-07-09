import pytest
import requests
import subprocess


class TestClient:
    HOST = 'http://127.0.0.1'
    PORT = 8001

    def get(self, url, *args, **kwargs):
        return requests.get(f"{self.HOST}:{self.PORT}{url}", *args, **kwargs)

    def post(self, url, *args, **kwargs):
        return requests.post(f"{self.HOST}:{self.PORT}{url}", *args, **kwargs)

    def put(self, url, *args, **kwargs):
        return requests.put(f"{self.HOST}:{self.PORT}{url}", *args, **kwargs)

    def delete(self, url, *args, **kwargs):
        return requests.delete(f"{self.HOST}:{self.PORT}{url}", *args, **kwargs)


app = subprocess.Popen(
    ['uvicorn', '--host', '0.0.0.0', '--port', f'{TestClient.PORT}', 'api.main:app'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
line = app.stderr.readline()
while b'Uvicorn running' not in line:
    line = app.stderr.readline()


@pytest.fixture(scope="session")
def setup():
    yield
    app.terminate()


@pytest.fixture()
def client(setup):
    return TestClient()
