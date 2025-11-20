# auth.py
import secrets
from typing import Dict

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# Hardcoded users (username -> password)
USERS_DB: Dict[str, str] = {
    "shrey": "password123",
    "test": "test123",
}

# token -> username mapping
TOKENS_DB: Dict[str, str] = {}

security = HTTPBearer()


def authenticate_user(username: str, password: str) -> str:
    """Validate username/password and return a new token."""
    stored_password = USERS_DB.get(username)
    if not stored_password or stored_password != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    # generate random token
    token = secrets.token_hex(32)
    TOKENS_DB[token] = username
    return token


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Get username from Bearer token."""
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid authentication scheme",
        )

    token = credentials.credentials
    username = TOKENS_DB.get(token)

    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    return username
