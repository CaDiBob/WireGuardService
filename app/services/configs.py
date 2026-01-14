import subprocess

from app.utils import file_operations


wg_config_template = """
[Peer]
PublicKey = {pubkey}
PresharedKey = {psk}
AllowedIps = {ip}
"""


class WireGuardConfig:
    server_config_file_path = "/etc/wireguard/wg0.conf"
    base_config = "/etc/wireguard/base.conf"
    command_reload = "systemctl reload wg-quick@wg0"

    def __init__(self, ip: str) -> None:
        self.ip = ip

    def _generate_wireguard_keys(self):
        privkey = (
            subprocess.check_output(
                "wg genkey",
                shell=True,
            ).decode("utf-8").strip()
        )
        pubkey = (
            subprocess.check_output(
                f"echo '{privkey}' | wg pubkey",
                shell=True,
            )
            .decode("utf-8")
            .strip()
        )
        psk = subprocess.check_output(
            "wg genkey",
            shell=True,
        ).decode("utf-8").strip()
        return privkey, pubkey, psk

    def _add_peer_to_server_config(
            self,
            pubkey: str,
            psk: str,
            ip: str,
    ) -> None:
        peer = wg_config_template.format(pubkey=pubkey, psk=psk, ip=ip)
        file_operations.write_to_file(
            self.server_config_file_path,
            peer,
            mode="a",
        )

    def _read_base_config(self) -> str:
        return file_operations.read_file(self.base_config).strip()

    def _reload_server_config(self) -> None:
        process = subprocess.Popen(self.command_reload, shell=True)
        process.communicate()

    def create_config(self) -> dict:
        privkey, pubkey, psk = self._generate_wireguard_keys()
        self._add_peer_to_server_config(pubkey, psk, self.ip)
        new_config = self._read_base_config().format(
            privkey=privkey, ip=self.ip, psk=psk
        )
        self._reload_server_config()
        return {"config": new_config}
