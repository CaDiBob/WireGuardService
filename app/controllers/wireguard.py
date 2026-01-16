import logging

from litestar import Controller, get, post, patch, Request, Response

from app.logger import Logger
from app.services.configs import WireGuardConfig
from app.services.wg_stats import WireGuardStatsService
from app.services.wg_client import WireGuardClient
from app.schemas.configs import (
    WireGuardAddPeerSchema,
    WireGuardUpdatePeerSchema,
)

logger = Logger('wireguard.log', log_level=logging.INFO)
wg_log = logger.get_logger()


class WireGuardController(Controller):

    path = '/vpn/wireguard'

    @post()
    async def add_peer(
        self,
        request: Request,
    ) -> Response:
        raw = await request.json()
        new = WireGuardAddPeerSchema.model_validate(raw)
        wireguard = WireGuardConfig()
        config = wireguard.create_config(new.ip)
        return Response(config)

    @get()
    async def get_stats(
        self,
        request: Request,
    ) -> Response:
        service = WireGuardStatsService()
        stats = service.get_stats()
        return Response(stats)

    @patch()
    async def update_peer(
        self,
        request: Request,
    ) -> Response:
        raw = await request.json()
        updated = WireGuardUpdatePeerSchema.model_validate(raw)
        pub_key = WireGuardConfig().get_pub_key(
            privkey=updated.private_key
        )
        service = WireGuardClient(pubkey=pub_key)
        if updated.action == "block":
            service.block()
        elif updated.action == "unblock":
            service.unblock(old_ip=updated.ip)
        return Response({"status": f"Client {updated.action}ed successfully."})
