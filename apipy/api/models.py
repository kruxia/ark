from pydantic.dataclasses import dataclass


@dataclass
class Status:
    code: int
    message: str


@dataclass
class HealthStatus:
    files: Status
    archive: Status
    database: Status
