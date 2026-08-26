import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from ..config import settings

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours


def _get_secret_key() -> str:
    if not settings.jwt_secret:
        raise RuntimeError(
            "JWT_SECRET environment variable is required. "
            "Set it to a secure random string in production."
        )
    return settings.jwt_secret


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(
        {"sub": str(user_id), "exp": expire},
        _get_secret_key(),
        algorithm=ALGORITHM,
    )


def decode_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, _get_secret_key(), algorithms=[ALGORITHM])
        return int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        return None