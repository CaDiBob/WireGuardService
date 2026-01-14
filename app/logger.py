import logging
from pathlib import Path


class Logger:
    def __init__(
            self,
            log_file_name: str,
            log_dir: str = 'logs',
            log_level: int = logging.DEBUG,
    ) -> None:
        self.log_file_name = log_file_name
        self.log_dir = Path(log_dir)
        self.log_level = log_level
        self.logger = self._setup_logger()

    @property
    def _file_path(self):
        self.log_dir.mkdir(parents=True, exist_ok=True)
        return self.log_dir.joinpath(self.log_file_name)

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger(self.log_file_name)
        file_handler = logging.FileHandler(self._file_path)
        file_handler.setLevel(self.log_level)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        if not logger.hasHandlers():
            logger.addHandler(file_handler)
        return logger

    def get_logger(self) -> logging.Logger:
        return self.logger
