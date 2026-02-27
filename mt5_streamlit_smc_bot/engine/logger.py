from __future__ import annotations

from datetime import datetime

from .config import LOGS_FILE, STORAGE_DIR


class BotLogger:
    def __init__(self) -> None:
        STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        LOGS_FILE.touch(exist_ok=True)

    def log(self, message: str) -> None:
        line = f"[{datetime.utcnow().isoformat()}] {message}\n"
        with LOGS_FILE.open("a", encoding="utf-8") as f:
            f.write(line)

    def read_last_lines(self, lines: int = 200) -> str:
        with LOGS_FILE.open("r", encoding="utf-8") as f:
            content = f.readlines()
        return "".join(content[-lines:])
