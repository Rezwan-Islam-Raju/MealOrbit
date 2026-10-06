import hashlib
import uuid
import datetime
import secrets

import bcrypt
import jwt

from pydantic_settings import BaseSettings, SettingsConfigDict



# SETTINGS


class Settings(BaseSettings):

    # APPLICATION

    APP_NAME: str = "Food Delivery API"
    ENVIRONMENT: str = "production"
    DEBUG: bool = False

    # DATABASE


    DATABASE_URL: str

    # REDIS


    REDIS_URL: str


    # JWT

    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_HOURS: int = 8
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7


    # SMTP


    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_FROM: str


    # SSL COMMERZ

    SSLCOMMERZ_STORE_ID: str
    SSLCOMMERZ_STORE_PASSWORD: str

    SSLCOMMERZ_IS_SANDBOX: bool

    SSLCOMMERZ_SUCCESS_URL: str
    SSLCOMMERZ_FAIL_URL: str
    SSLCOMMERZ_CANCEL_URL: str
    SSLCOMMERZ_IPN_URL: str


    # PYDANTIC SETTINGS

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# SETTINGS INSTANCE


settings = Settings()


# DATABASE

DATABASE_URL = settings.DATABASE_URL

# Render / hosted PostgreSQL may provide:
# postgresql://...
# SQLAlchemy async requires:
# postgresql+asyncpg://...

if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+asyncpg://",
        1,
    )



# REDIS


REDIS_URL = settings.REDIS_URL



# JWT


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM



# SMTP


SMTP_HOST = settings.SMTP_HOST
SMTP_PORT = settings.SMTP_PORT
SMTP_USER = settings.SMTP_USER
SMTP_PASSWORD = settings.SMTP_PASSWORD
SMTP_FROM = settings.SMTP_FROM


# SSL COMMERZ


SSLCOMMERZ_STORE_ID = settings.SSLCOMMERZ_STORE_ID
SSLCOMMERZ_STORE_PASSWORD = settings.SSLCOMMERZ_STORE_PASSWORD

SSLCOMMERZ_IS_SANDBOX = settings.SSLCOMMERZ_IS_SANDBOX

SSLCOMMERZ_SUCCESS_URL = settings.SSLCOMMERZ_SUCCESS_URL
SSLCOMMERZ_FAIL_URL = settings.SSLCOMMERZ_FAIL_URL
SSLCOMMERZ_CANCEL_URL = settings.SSLCOMMERZ_CANCEL_URL
SSLCOMMERZ_IPN_URL = settings.SSLCOMMERZ_IPN_URL



# SSL COMMERZ API URL


if SSLCOMMERZ_IS_SANDBOX:

    SSLCOMMERZ_PAYMENT_URL = (
        "https://sandbox-gw.sslcommerz.com/"
        "gwprocess/v4/api.php"
    )

    SSLCOMMERZ_VALIDATION_URL = (
        "https://sandbox-gw.sslcommerz.com/"
        "validator/api/validationserverAPI.php"
    )

else:

    SSLCOMMERZ_PAYMENT_URL = (
        "https://securepay.sslcommerz.com/"
        "gwprocess/v4/api.php"
    )

    SSLCOMMERZ_VALIDATION_URL = (
        "https://securepay.sslcommerz.com/"
        "validator/api/validationserverAPI.php"
    )



# ACCESS TOKEN


def encode_access_token(user_id: int, email: str):

    now = datetime.datetime.now(datetime.timezone.utc)

    exp = now + datetime.timedelta(
        hours=settings.ACCESS_TOKEN_EXPIRE_HOURS
    )

    payload = {
        "user_id": user_id,
        "email": email,
        "token_type": "access",
        "iat": now,
        "exp": exp,
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return token



# DECODE ACCESS TOKEN


def decode_access_token(token: str):

    return jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
    )



# REFRESH TOKEN


def encode_refresh_token(user_id: int):

    now = datetime.datetime.now(datetime.timezone.utc)

    exp = now + datetime.timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    payload = {
        "user_id": user_id,
        "token_type": "refresh",
        "iat": now,
        "exp": exp,
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return token



# DECODE AUTH TOKEN


def decode_auth_token(token: str):

    try:

        decoded = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        return decoded

    except jwt.ExpiredSignatureError:

        return None

    except jwt.InvalidTokenError:

        return None


# PASSWORD HASH


def hash_password(password: str):

    salt = bcrypt.gensalt()

    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        salt,
    )

    return password_hash.decode("utf-8")



# PASSWORD VERIFY


def verify_password(
    password: str,
    hashed_password: str,
):

    try:

        return bcrypt.checkpw(
            password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )

    except (ValueError, AttributeError):

        return False



# ACTIVATION TOKEN


def generate_activation_token():

    return secrets.token_urlsafe(32)


def hash_activation_token(token: str):

    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()



# REFRESH TOKEN HASH


def generate_refresh_token():

    return secrets.token_urlsafe(64)


def hash_refresh_token(token: str):

    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


# RESET TOKEN


def generate_reset_token():

    return secrets.token_urlsafe(32)


def hash_reset_token(token: str):

    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()



# TRANSACTION ID


def generate_transaction_id():

    return f"TXN-{uuid.uuid4().hex[:20].upper()}"