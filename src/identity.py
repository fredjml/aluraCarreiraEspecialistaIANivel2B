"""Identidade JWT para o protótipo Bytebank, sem dados de pessoas reais."""
from __future__ import annotations

import os
from dataclasses import dataclass


ROLE_LEVELS = {
    "cliente": frozenset({"publico"}),
    "atendente": frozenset({"publico", "interno"}),
    "analista": frozenset({"publico", "interno", "restrito"}),
    "aprovador": frozenset({"publico", "interno"}),
    "administrador": frozenset({"publico", "interno", "restrito"}),
}


class IdentityError(ValueError):
    """Token ausente, inválido ou incompatível com a configuração."""


@dataclass(frozen=True)
class Identity:
    subject: str
    roles: frozenset[str]
    allowed_levels: frozenset[str]

    @property
    def can_approve(self) -> bool:
        return bool({"aprovador", "administrador"} & self.roles)


ANONYMOUS = Identity("anonymous", frozenset(), frozenset({"publico"}))


def authenticate_bearer(token: str | None) -> Identity:
    """Valida assinatura, emissor, audiência e expiração de um JWT configurado."""
    if not token:
        return ANONYMOUS
    try:
        import jwt
    except ImportError as error:
        raise IdentityError("PyJWT não está instalado") from error

    issuer = os.getenv("BYTEBANK_JWT_ISSUER", "").strip()
    audience = os.getenv("BYTEBANK_JWT_AUDIENCE", "").strip()
    jwks_url = os.getenv("BYTEBANK_JWT_JWKS_URL", "").strip()
    key = os.getenv("BYTEBANK_JWT_PUBLIC_KEY", "").strip() or os.getenv(
        "BYTEBANK_JWT_SHARED_SECRET", ""
    ).strip()
    if not issuer or not audience or (not key and not jwks_url):
        raise IdentityError("validação JWT não configurada")
    try:
        if jwks_url:
            signing_key = jwt.PyJWKClient(jwks_url).get_signing_key_from_jwt(token).key
        else:
            signing_key = key
        claims = jwt.decode(
            token,
            signing_key,
            algorithms=[item.strip() for item in os.getenv("BYTEBANK_JWT_ALGORITHMS", "RS256,HS256").split(",")],
            issuer=issuer,
            audience=audience,
            options={"require": ["exp", "sub", "iss", "aud"]},
        )
    except Exception as error:
        raise IdentityError("token JWT inválido") from error
    roles = frozenset(str(role) for role in claims.get("roles", []))
    levels = frozenset().union(*(ROLE_LEVELS.get(role, frozenset()) for role in roles))
    if not levels:
        raise IdentityError("token sem papel autorizado")
    return Identity(str(claims["sub"]), roles, levels)