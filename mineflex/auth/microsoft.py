"""Microsoft / Xbox Live authentication provider stub and token flow."""

from __future__ import annotations

import uuid
from typing import Optional

from mineflex.auth.base import AuthProvider, Session
from mineflex.errors import AuthenticationError


class MicrosoftAuthProvider(AuthProvider):
    """Microsoft and Xbox Live OAuth token authenticator."""

    def __init__(self, access_token: Optional[str] = None) -> None:
        self.access_token = access_token

    async def authenticate(self, username: str, **kwargs) -> Session:
        token = kwargs.get("access_token") or self.access_token
        if not token:
            raise AuthenticationError(
                "Microsoft authentication requires an access_token or interactive OAuth login flow."
            )

        # In production this queries Mojang profile API: GET https://api.minecraftservices.com/minecraft/profile
        # If token is provided, construct verified online session
        return Session(
            username=username,
            player_uuid=uuid.uuid4(),
            access_token=token,
            is_online=True,
        )
