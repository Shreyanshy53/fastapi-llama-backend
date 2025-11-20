# storage/history.py
import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from schemas import HistoryItem


class HistoryStore:
    def __init__(self, file_path: str = "history.json") -> None:
        self.file_path = Path(file_path)
        self.lock = threading.Lock()
        self._ensure_file()

    def _ensure_file(self) -> None:
        if not self.file_path.exists():
            self.file_path.write_text(json.dumps({}), encoding="utf-8")

    def _read_data(self) -> Dict[str, List[Dict[str, Any]]]:
        raw = self.file_path.read_text(encoding="utf-8")
        if not raw.strip():
            return {}
        return json.loads(raw)

    def _write_data(self, data: Dict[str, List[Dict[str, Any]]]) -> None:
        self.file_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def log_interaction(self, username: str, prompt: str, response: str) -> HistoryItem:
        timestamp = datetime.utcnow().isoformat()

        record = {
            "timestamp": timestamp,
            "prompt": prompt,
            "response": response,
        }

        with self.lock:
            data = self._read_data()
            user_history = data.get(username, [])
            user_history.append(record)
            data[username] = user_history
            self._write_data(data)

        return HistoryItem(
            timestamp=datetime.fromisoformat(timestamp),
            prompt=prompt,
            response=response,
        )

    def get_history(self, username: str) -> List[HistoryItem]:
        with self.lock:
            data = self._read_data()
            user_history = data.get(username, [])

        return [
            HistoryItem(
                timestamp=datetime.fromisoformat(item["timestamp"]),
                prompt=item["prompt"],
                response=item["response"],
            )
            for item in user_history
        ]
