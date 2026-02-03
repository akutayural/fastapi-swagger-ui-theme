from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


security = HTTPBearer(auto_error=False)

DEMO_USER = "admin"
DEMO_PASS = "admin"
DEMO_TOKEN = "dev-token"


def authenticate_user(username: str, password: str) -> bool:
    return username == DEMO_USER and password == DEMO_PASS


def require_token(
    creds: HTTPAuthorizationCredentials | None = Depends(security),
) -> str:
    if creds is None or creds.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )

    if creds.credentials != DEMO_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    return creds.credentials
