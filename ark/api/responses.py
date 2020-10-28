import typing
import orjson
from pydantic import BaseModel
from starlette.responses import Response


class JSONResponse(Response):
    """
    A custom Response class to provide a JSON response.

    * Uses the `orjson` library for speed and to support more of the standard data types
      (datetime, UUID)
    * Support rendering pydantic BaseModel classes directly (by calling `.dict()` on it)
    """

    media_type = "application/json"

    def render(self, content: typing.Any) -> bytes:
        """
        Render the given content using orjson. If the content is a pydantic BaseModel,
        then call its `.dict()` method to pass a dict to orjson.
        """
        if isinstance(content, BaseModel):
            return orjson.dumps(content.dict())
        else:
            return orjson.dumps(content)
