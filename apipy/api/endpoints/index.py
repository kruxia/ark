from dataclasses import asdict
from api.responses import ORJSONResponse
from api.models import Status
from starlette.endpoints import HTTPEndpoint


class Index(HTTPEndpoint):
    async def get(self, request):
        return ORJSONResponse(
            asdict(Status(code=200, message='Welcome to the Ark API'))
        )
