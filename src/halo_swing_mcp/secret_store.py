"""Encrypted local credential storage for Binance COIN-M trading."""

from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from halo_swing_mcp.audit import utc_now
from halo_swing_mcp.config import get_settings


SCHEMA_VERSION = "binance_credentials.v1"
KDF_ITERATIONS = 390_000


@dataclass(frozen=True)
class BinanceCredentials:
    api_key: str
    api_secret: str


def save_binance_credentials(
    api_key: str,
    api_secret: str,
    passphrase: str,
    credentials_path: str | None = None,
) -> dict[str, Any]:
    """Encrypt Binance API credentials into a local ignored JSON file."""

    _validate_secret_inputs(api_key, api_secret, passphrase)
    path = resolve_credentials_path(credentials_path)
    salt = os.urandom(16)
    fernet = Fernet(_derive_key(passphrase, salt))
    token = fernet.encrypt(
        json.dumps(
            {
                "api_key": api_key,
                "api_secret": api_secret,
            },
            sort_keys=True,
        ).encode("utf-8")
    )
    existing = _read_existing(path)
    timestamp = utc_now()
    payload = {
        "schema_version": SCHEMA_VERSION,
        "provider": "binance_coin_m_futures",
        "created_at": existing.get("created_at", timestamp),
        "updated_at": timestamp,
        "api_key_hint": _mask_api_key(api_key),
        "kdf": {
            "name": "PBKDF2HMAC-SHA256",
            "iterations": KDF_ITERATIONS,
            "salt_b64": base64.b64encode(salt).decode("ascii"),
        },
        "cipher": {
            "name": "Fernet",
            "token": token.decode("ascii"),
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    try:
        path.chmod(0o600)
    except OSError:
        pass
    return get_binance_credentials_status(str(path))


def get_binance_credentials_status(credentials_path: str | None = None) -> dict[str, Any]:
    """Return safe credential metadata without exposing secrets."""

    path = resolve_credentials_path(credentials_path)
    if not path.exists():
        return {
            "configured": False,
            "provider": "binance_coin_m_futures",
            "credentials_path": str(path),
            "live_data_required": False,
        }
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {
        "configured": True,
        "provider": payload.get("provider", "binance_coin_m_futures"),
        "credentials_path": str(path),
        "api_key_hint": payload.get("api_key_hint"),
        "created_at": payload.get("created_at"),
        "updated_at": payload.get("updated_at"),
        "kdf": {
            "name": payload.get("kdf", {}).get("name"),
            "iterations": payload.get("kdf", {}).get("iterations"),
        },
        "cipher": {
            "name": payload.get("cipher", {}).get("name"),
        },
        "live_data_required": False,
    }


def load_binance_credentials(
    passphrase: str,
    credentials_path: str | None = None,
) -> BinanceCredentials:
    """Decrypt Binance API credentials with a caller-provided passphrase."""

    if not passphrase:
        raise ValueError("credential passphrase is required.")
    path = resolve_credentials_path(credentials_path)
    if not path.exists():
        raise ValueError("encrypted Binance credentials are not configured.")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported Binance credential schema.")
    salt = base64.b64decode(payload["kdf"]["salt_b64"])
    token = payload["cipher"]["token"].encode("ascii")
    fernet = Fernet(_derive_key(passphrase, salt))
    try:
        decrypted = fernet.decrypt(token)
    except InvalidToken as exc:
        raise ValueError("invalid Binance credential passphrase.") from exc
    values = json.loads(decrypted.decode("utf-8"))
    return BinanceCredentials(
        api_key=str(values["api_key"]),
        api_secret=str(values["api_secret"]),
    )


def resolve_credentials_path(credentials_path: str | None = None) -> Path:
    return Path(credentials_path or get_settings().binance_credentials_path)


def _derive_key(passphrase: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=KDF_ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(passphrase.encode("utf-8")))


def _validate_secret_inputs(api_key: str, api_secret: str, passphrase: str) -> None:
    if not api_key.strip():
        raise ValueError("api_key is required.")
    if not api_secret.strip():
        raise ValueError("api_secret is required.")
    if len(passphrase) < 8:
        raise ValueError("passphrase must be at least 8 characters.")


def _mask_api_key(api_key: str) -> str:
    if len(api_key) <= 9:
        return "[CONFIGURED]"
    return f"{api_key[:5]}...{api_key[-4:]}"


def _read_existing(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
