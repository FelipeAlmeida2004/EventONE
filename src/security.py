from typing import Optional

from fastapi import Request
from src.config import settings as s
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import time

def sign_jwt(user_id: int) -> dict[str, str]:
    expiration_time = int(time.time()) + s.access_token_expire_minutes * 60
    payload = {
        "user_id": user_id,
        "exp": expiration_time
    }

    token = jwt.encode(payload, s.secret_key.get_secret_value(), algorithm=s.algorithm)
    return {"access_token": token}


def decode_jwt(token: str) -> dict:
    try:
        return jwt.decode(token, s.secret_key.get_secret_value(), algorithms=[s.algorithm])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Token expirou")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")
    

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)
    
    async def __call__(self, request: Request) -> str:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if not credentials or not credentials.scheme == "Bearer":
            raise HTTPException(status_code=403, detail="Não autorizado")
        decoded_token = decode_jwt(credentials.credentials)

        return decoded_token.get("user_id")