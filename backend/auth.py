"""
User identity extraction for Bright AEO Engine.

Resolution order on every request:
  1. X-MS-CLIENT-PRINCIPAL header (Azure App Service Easy Auth)
  2. DEV_USER env var (local development fallback)
  3. HTTP 401

Usage:
    from auth import CurrentUser, get_current_user
    from fastapi import Depends

    @router.post("/something")
    async def handler(user: CurrentUser = Depends(get_current_user)):
        ...
"""

import base64
import hashlib
import json
import os
import warnings
from dataclasses import dataclass, asdict

from fastapi import Depends, HTTPException, Request

from core.logging import get_logger

logger = get_logger(__name__)

# Claim type URIs used by Azure AD / Entra ID
_CLAIM_ALIASES = {
    "name": [
        "name",
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name",
    ],
    "email": [
        "preferred_username",
        "upn",
        "email",
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress",
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/upn",
    ],
    "oid": [
        "oid",
        "http://schemas.microsoft.com/identity/claims/objectidentifier",
    ],
}


@dataclass(frozen=True)
class CurrentUser:
    name: str
    email: str
    oid: str
    source: str  # "easy_auth" | "dev_fallback"

    def to_dict(self) -> dict:
        return asdict(self)

    def attribution(self) -> dict:
        """Compact form for embedding in run JSON and audit events."""
        return {"name": self.name, "email": self.email, "oid": self.oid}


def _extract_claim(claims: list[dict], aliases: list[str]) -> str:
    for alias in aliases:
        for c in claims:
            if c.get("typ") == alias:
                return c.get("val", "")
    return ""


def _decode_principal(header: str) -> CurrentUser:
    # Base64url padding is stripped by Azure — add it back before decoding
    padded = header + "=" * (-len(header) % 4)
    payload = json.loads(base64.b64decode(padded))
    claims = payload.get("claims", [])

    name  = _extract_claim(claims, _CLAIM_ALIASES["name"])
    email = _extract_claim(claims, _CLAIM_ALIASES["email"]).lower()
    oid   = _extract_claim(claims, _CLAIM_ALIASES["oid"])

    if not email:
        email = name.lower().replace(" ", ".") + "@unknown"
    if not name:
        name = email.split("@")[0]

    return CurrentUser(name=name, email=email, oid=oid, source="easy_auth")


def _parse_dev_user(dev: str) -> CurrentUser:
    dev = dev.strip()
    if "<" in dev and ">" in dev:
        name  = dev.split("<")[0].strip()
        email = dev.split("<")[1].rstrip(">").strip().lower()
    else:
        email = dev.lower()
        local = email.split("@")[0]
        name  = " ".join(p.capitalize() for p in local.replace(".", " ").replace("_", " ").split())

    # Deterministic synthetic OID so dev records are distinguishable from prod
    oid = "dev:" + hashlib.sha256(email.encode()).hexdigest()[:16]
    return CurrentUser(name=name, email=email, oid=oid, source="dev_fallback")


def get_current_user(request: Request) -> CurrentUser:
    header = request.headers.get("X-MS-CLIENT-PRINCIPAL")
    if header:
        try:
            return _decode_principal(header)
        except Exception as exc:
            logger.warning("Failed to decode X-MS-CLIENT-PRINCIPAL", extra={"context": {"error": str(exc)}})

    dev = os.getenv("DEV_USER")
    if dev:
        logger.warning(
            "Using DEV_USER fallback — Easy Auth not active",
            extra={"context": {"dev_user": dev}},
        )
        return _parse_dev_user(dev)

    raise HTTPException(status_code=401, detail="Not authenticated")
