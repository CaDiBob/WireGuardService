from enum import Enum

from pydantic import BaseModel


class WireGuardActionEnum(str, Enum):
    block = "block"
    unblock = "unblock"


class WireGuardAddPeerSchema(BaseModel):
    ip: str


class ConfigResponceSchema(BaseModel):
    config: str


class WireGuardUpdatePeerSchema(BaseModel):
    action: WireGuardActionEnum
    private_key: str | None = None
    ip: str | None = None
