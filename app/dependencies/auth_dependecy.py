from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from starlette import status

from config.config import decode_access_token


async def require_user_id(credentials:HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    try:
        payload = decode_access_token(credentials.credentials)
        return payload["user_id"]
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Unauthorized")