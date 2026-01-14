from litestar import Litestar, get

from app.controllers.wireguard import WireGuardController


@get("/")
async def hello_world() -> dict[str, str]:
    """Keeping the tradition alive with hello world."""
    return {"hello": "world"}


app = Litestar(route_handlers=[WireGuardController, hello_world])
