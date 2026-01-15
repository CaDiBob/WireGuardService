import logging

from litestar import Controller, post, Request, Response

from app.logger import Logger
from app.services.configs import WireGuardConfig
from app.schemas.configs import SWireGuard

logger = Logger('wireguard.log', log_level=logging.INFO)
wg_log = logger.get_logger()


class WireGuardController(Controller):
    '''
    Обрабатывает запрос пользователя
    '''

    path = '/vpn/wireguard'

    @post()
    async def add_peer(
        self,
        request: Request,
    ) -> Response:
        raw = await request.json()
        new = SWireGuard.model_validate(raw)
        wireguard = WireGuardConfig(new.ip)
        config = wireguard.create_config()
        return Response(config)
