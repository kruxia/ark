from api.responses import JSONResponse
from api.models import Status
from starlette.endpoints import HTTPEndpoint


class Index(HTTPEndpoint):
    async def get(self, request):
        return JSONResponse(Status(code=200, message='Welcome to the Ark API'))
