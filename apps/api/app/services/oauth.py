"""OAuth provider integration placeholders."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class OAuthProviderConfig:
    """Configuration for an OAuth provider."""

    name: str
    client_id: str
    client_secret: str


class OAuthProvider:
    """Simplified OAuth provider representation for bootstrapping."""

    def __init__(self, config: OAuthProviderConfig) -> None:
        self.config = config

    def authorization_url(self, redirect_uri: str) -> str:
        """Return a dummy authorization URL."""

        return (
            f"https://auth.example.com/{self.config.name}?redirect_uri={redirect_uri}"
        )
