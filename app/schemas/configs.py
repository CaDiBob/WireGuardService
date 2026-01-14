from pydantic import BaseModel


class SWireGuard(BaseModel):
    ip: str


class SConfig(BaseModel):
    config: str
