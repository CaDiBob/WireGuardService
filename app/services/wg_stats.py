import subprocess
import sys
import logging
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)


@dataclass
class Client:
    allowed_ips: str
    endpoint: Optional[str] = None
    latest_handshake: Optional[int] = None
    transfer: Optional[int] = None


@dataclass
class ServiceConfig:
    output_dir: Path
    output_filename: str
    command: list[str] = field(
        default_factory=lambda: ["wg", "show", "all", "dump"],
    )


class CommandExecutor:
    @staticmethod
    def run(command: list[str], as_sudo: bool = True) -> str:
        if as_sudo:
            command.insert(0, "sudo")
        logging.info(f"Выполнение команды: {' '.join(command)}")
        try:
            process_result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8",
            )
            return process_result.stdout
        except FileNotFoundError:
            logging.error(f"Ошибка: команда '{command[0]}' не найдена.")
            raise
        except subprocess.CalledProcessError as e:
            logging.error(f"Ошибка при выполнении команды: {e.stderr}")
            raise


class DumpParser:
    """Парсит вывод 'wg show dump' в структурированные данные."""

    def parse(self, raw_output: str):
        if not raw_output.strip():
            logging.warning("Получен пустой вывод от команды.")
            return {}
        lines = raw_output.splitlines()
        clients = {}
        for line in lines:
            parts = line.split("\t")
            min_count_parts = 5  # Минимальное количество полей
            if len(parts) <= min_count_parts:
                continue
            pub_key, client = self._parse_line(parts=parts)
            if client.latest_handshake:
                clients[pub_key] = asdict(client)
        return clients

    def _parse_line(self, parts: list[str]) -> tuple[str, Client]:
        (
            _,
            pub_key,
            _,
            endpoint,
            allowed_ips,
            latest_handshake,
            transfer_rx,
            transfer_tx,
            *_,
        ) = parts
        return pub_key, Client(
            endpoint=endpoint,
            allowed_ips=allowed_ips,
            latest_handshake=int(latest_handshake),
            transfer=int(transfer_rx) + int(transfer_tx),
        )


class WireGuardStatsService:

    def __init__(self):
        self.config = ServiceConfig(
            output_dir=Path("wireguard-json"),
            output_filename="wg.json",
        )
        self.output_path = self.config.output_dir / self.config.output_filename

    def get_stats(self) -> bool:
        raw_output = CommandExecutor.run(self.config.command)
        clients = DumpParser().parse(raw_output)
        stats = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": clients
        }

        return stats
