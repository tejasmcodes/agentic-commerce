import json
from pathlib import Path


AUDIT_FILE = Path(__file__).resolve().parents[3] / "merchant_audit_log.json"


def write_merchant_audit_log(entry: dict) -> None:
    """Write a merchant campaign audit entry."""

    logs = []

    if AUDIT_FILE.exists() and AUDIT_FILE.stat().st_size > 0:
        try:
            with open(AUDIT_FILE, "r") as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            logs = []

    logs.append(entry)

    with open(AUDIT_FILE, "w") as f:
        json.dump(logs, f, indent=2)