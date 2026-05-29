#!/usr/bin/env python3
"""Quick check: can this machine reach UQC (Socket.IO on SERVER_HOST:SERVER_PORT)?"""

from __future__ import annotations

import os
import socket
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from qchem_stack.backends.uqc_env import load_repo_dotenv  # noqa: E402


def main() -> int:
    load_repo_dotenv()
    host = os.environ.get("SERVER_HOST", "cloud.unitaryqubit.com")
    port = int(os.environ.get("SERVER_PORT", "8003"))
    token = (os.environ.get("UQC_API_TOKEN") or os.environ.get("USER_TOKEN") or "").strip()

    print(f"TCP {host}:{port} ...", end=" ", flush=True)
    try:
        with socket.create_connection((host, port), timeout=8):
            print("OK")
    except OSError as exc:
        print(f"FAIL ({exc})")
        print("Hint: set SERVER_HOST in .env (e.g. 192.168.110.148) on company intranet.")
        return 1

    if not token:
        print("WARN: no UQC_API_TOKEN in .env — API login not tested.")
        return 2

    from uqc_client import UQC

    print("Socket.IO + get_chips ...", end=" ", flush=True)
    try:
        client = UQC(token=token)
        chips = client.get_chips()
        print("OK", list(chips.keys()) if isinstance(chips, dict) else chips)
    except Exception as exc:
        print(f"FAIL ({exc})")
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
