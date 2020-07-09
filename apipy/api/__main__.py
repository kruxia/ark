from fastapi import FastAPI
from fastapi.responses import ORJSONResponse


app = FastAPI()


@app.get("/", response_class=ORJSONResponse)
def index():
    return {
        "status": 200,
        "message": "Welcome to the Ark API",
    }
