import typing
import orjson
from pydantic import BaseModel
from starlette.responses import Response


class JSONResponse(Response):
    media_type = "application/json"

    def render(self, content: typing.Any) -> bytes:
        # support rendering pydantic models directly
        if isinstance(content, BaseModel):
            return orjson.dumps(content.dict())
        else:
            return orjson.dumps(content)
