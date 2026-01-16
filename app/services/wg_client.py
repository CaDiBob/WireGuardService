import logging
import os
import subprocess

from app.logger import Logger

logger = Logger('wireguard_client.log', log_level=logging.INFO)
log = logger.get_logger()


WG_INT_NAME = os.getenv("WG_INT_NAME", "wg0")
WG_AS_SUDO = bool(os.getenv("WG_AS_SUDO", True))
WG_BIN_PATH = os.getenv("WG_BIN_PATH", "/usr/bin/wg")
WG_QUICK_PATH = os.getenv("WG_BIN_PATH", "/usr/bin/wg-quick")


class WireGuardClient:
    WG_PUBKEY_LEN = 44
    WG_EXEC_TIMEOUT = 50.0
    BLOCK_IP = "127.0.0.2"

    def __init__(self, pubkey: str, interface: str = WG_INT_NAME):
        if isinstance(pubkey, str):
            if pubkey[-1] == "=" and \
                    len(pubkey) == self.WG_PUBKEY_LEN:

                self.pubkey = pubkey
            else:
                raise ValueError(
                    f"Public key should be {self.WG_PUBKEY_LEN} "
                    f"symbols long and end with ="
                )
        else:
            raise ValueError("Public key should be a string.")

        self.interface = interface
        log.info("Pubkey: %s  Interface: %s", pubkey, interface)

    def _get_ip(self, sudo: bool = WG_AS_SUDO) -> str | None:
        cmd = [WG_BIN_PATH, "show", self.interface, "dump"]
        if sudo:
            cmd.insert(0, "sudo")

        log.info("Running command: %s", cmd)
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=self.WG_EXEC_TIMEOUT,
            check=False,
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"{cmd!r} failed (code {proc.returncode}): "
                f"{proc.stderr.strip()}"
            )
        for line in proc.stdout.splitlines():
            cols = line.split()
            if self.pubkey in cols:
                if len(cols) >= 4:
                    log.info(
                        "Found WG allowedip for client %s: %s",
                        self.pubkey,
                        cols[3],
                    )
                    return cols[3]
                return None
        return None

    def _change_ip(self, new_ip: str, sudo: bool = WG_AS_SUDO) -> str | bool:
        ch_cmd = [
            WG_BIN_PATH,
            "set",
            self.interface,
            "peer",
            self.pubkey,
            "allowed-ips",
            f"{new_ip}/32",
        ]
        save_cmd = [WG_QUICK_PATH, "save", self.interface]
        if sudo:
            ch_cmd.insert(0, "sudo")
            save_cmd.insert(0, "sudo")

        log.info("Running command: %s", ch_cmd)
        ch_int = subprocess.run(
            ch_cmd,
            capture_output=True,
            text=True,
            timeout=self.WG_EXEC_TIMEOUT,
            check=False,
        )

        log.info("Running command: %s", save_cmd)
        save_int = subprocess.run(
            save_cmd,
            capture_output=True,
            text=True,
            timeout=self.WG_EXEC_TIMEOUT,
            check=False,
        )

        if ch_int.returncode != 0:
            raise RuntimeError(
                f"{ch_cmd!r} failed (code {ch_int.returncode}): "
                f"{ch_int.stderr.strip()}"
            )
        if save_int.returncode != 0:
            raise RuntimeError(
                f"{save_cmd!r} failed (code {save_int.returncode}): "
                f"{save_int.stderr.strip()}"
            )
        return True

    def block(self) -> bool:
        """
        usage: WireguardClient\
        ("6cCLfSYbyPcRODrH3yNuxiaqNZ212345YpzB6LAb3nM=").block()
        """
        log.warning("Blocking client %s", self.pubkey)
        return self._change_ip(self.BLOCK_IP)

    def unblock(self, old_ip: str) -> bool:
        """
        usage: WireguardClient\
        ("6cCLfSYbyPcRODrH3yNuxiaqNZ212345YpzB6LAb3nM=").unblock("10.64.1.7")
        """
        log.warning("Unblocking client %s", self.pubkey)
        return self._change_ip(old_ip)
