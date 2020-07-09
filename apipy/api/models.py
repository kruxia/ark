from pydantic import BaseModel


class Status(BaseModel):
    code: int
    message: str


class HealthStatus(BaseModel):
    files: Status
    archive: Status
    database: Status
