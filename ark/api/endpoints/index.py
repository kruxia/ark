from api.responses import JSONResponse
from api.types import Result
from starlette.endpoints import HTTPEndpoint


class Index(HTTPEndpoint):
    """
    Endpoint for the root of the API. TODO: After setting up API docs, point to it.
    """

    async def get(self, request):
        """
        Return 200 OK with a welcome message.
        """
        return JSONResponse(Result(status=200, message='Welcome to the Ark API'))
