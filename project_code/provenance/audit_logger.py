import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

class ProvenanceAuditLogger:
    """
    Maintains immutable-style, tamper-evident audit logs for every analyst action
    and inference execution for SIH-227.
    """

    def __init__(self, log_file: Optional[str] = None):
        from project_code.config import LOGS_DIR
        self.log_file = Path(log_file) if log_file else (LOGS_DIR / "audit_provenance.jsonl")
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def compute_file_hash(filepath: str) -> str:
        """Computes SHA-256 hash of a file (e.g. model checkpoint)."""
        p = Path(filepath)
        if not p.exists():
            return "FILE_NOT_FOUND"
        sha256 = hashlib.sha256()
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def log_decision(
        self,
        tile_id: str,
        dataset_name: str,
        action: str, # 'CONFIRM', 'REJECT', 'NEEDS_REVIEW'
        analyst_id: str = "analyst_primary",
        model_version: str = "SiameseResNet18-v1.0",
        model_checkpoint_path: Optional[str] = None,
        threshold: float = 0.50,
        change_percentage: float = 0.0,
        notes: str = ""
    ) -> Dict[str, Any]:
        """Logs an analyst decision with cryptographic audit record."""
        now = datetime.now(timezone.utc).isoformat()
        model_hash = self.compute_file_hash(model_checkpoint_path) if model_checkpoint_path else "N/A"

        payload = {
            "timestamp": now,
            "analyst_id": analyst_id,
            "action": action.upper(),
            "tile_id": tile_id,
            "dataset_name": dataset_name,
            "model_version": model_version,
            "model_hash": model_hash,
            "threshold": threshold,
            "change_percentage": change_percentage,
            "notes": notes
        }

        # Tamper-evident record hash
        record_string = json.dumps(payload, sort_keys=True)
        record_hash = hashlib.sha256(record_string.encode("utf-8")).hexdigest()
        payload["record_hash"] = record_hash

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")

        return payload

    def get_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieves recent audit log records."""
        if not self.log_file.exists():
            return []
        records = []
        with open(self.log_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line.strip()))
        return records[-limit:]
