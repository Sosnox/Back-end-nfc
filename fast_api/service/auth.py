from fastapi import HTTPException
import hashlib
import os
from jose import jwt
from datetime import datetime, timedelta, timezone

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        sha256 = hashlib.sha256()
        sha256.update(password.encode('utf-8'))
        return sha256.hexdigest()

    @staticmethod
    def create_token(uid: str, exp_duration: timedelta,role:str) -> str:
        payload = {
            "uid": uid,
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + exp_duration ,
            "role": role
        }
        return AuthService.encode_jwt(payload)

    @staticmethod
    def encode_jwt(payload: dict) -> str:
        secret = os.getenv("JWT_SECRET", "your_default_secret")
        algorithm = "HS256"
        return jwt.encode(payload, secret, algorithm=algorithm)

    @staticmethod
    def decode_jwt(token: str) -> str:
        secret = os.getenv("JWT_SECRET", "your_default_secret")
        algorithm = "HS256"
        try:
            decoded = jwt.decode(token, secret, algorithms=[algorithm])
            return decoded
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Could not validate token")
    
    @staticmethod
    def isAdmin(token: str) -> bool:
        jwt = AuthService.decode_jwt(token)
        if jwt['role'] == "admin":
            return True
        else:
            raise HTTPException(status_code=401, detail=f"wrong role")

    @staticmethod
    def isSuperAdmin(token: str) -> bool:
        jwt = AuthService.decode_jwt(token)
        if jwt['role'] == "super_admin":
            return True
        else:
            raise HTTPException(status_code=401, detail=f"wrong role")

    

