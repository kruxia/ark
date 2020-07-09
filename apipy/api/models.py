from pydantic.dataclasses import dataclass


@dataclass
class StatusMessage:
    status: int
    message: str


@dataclass
class HealthStatus:
    files: StatusMessage
    archive: StatusMessage
    database: StatusMessage
