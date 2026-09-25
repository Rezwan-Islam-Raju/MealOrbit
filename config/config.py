import hashlib
import uuid

import bcrypt
import jwt
import datetime
import os
from dotenv import load_dotenv
import secrets

load_dotenv()



# DATABASE


DATABASE_URL = os.getenv("DATABASE_URL")



# JWT


SECRET_KEY = os.getenv("SECRET_KEY")

ALGORITHM = "HS256"



# SMTP SERVER


SMTP_HOST = os.getenv("SMTP_HOST")

SMTP_PORT = int(
    os.getenv(
        "SMTP_PORT",
        "25"
    )
)

SMTP_USER = os.getenv(
    "SMTP_USER"
)

SMTP_PASSWORD = os.getenv(
    "SMTP_PASSWORD"
)

SMTP_FROM = os.getenv(
    "SMTP_FROM"
)




# SSL COMMERZ


SSLCOMMERZ_STORE_ID = os.getenv(
    "SSLCOMMERZ_STORE_ID"
)

SSLCOMMERZ_STORE_PASSWORD = os.getenv(
    "SSLCOMMERZ_STORE_PASSWORD"
)

SSLCOMMERZ_IS_SANDBOX = os.getenv(
    "SSLCOMMERZ_IS_SANDBOX",
    "true"
).lower() == "true"


SSLCOMMERZ_SUCCESS_URL = os.getenv(
    "SSLCOMMERZ_SUCCESS_URL"
)

SSLCOMMERZ_FAIL_URL = os.getenv(
    "SSLCOMMERZ_FAIL_URL"
)

SSLCOMMERZ_CANCEL_URL = os.getenv(
    "SSLCOMMERZ_CANCEL_URL"
)

SSLCOMMERZ_IPN_URL = os.getenv(
    "SSLCOMMERZ_IPN_URL"
)



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
    exp = now + datetime.timedelta(hours=8)

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
        algorithm=ALGORITHM
    )

    return token

# Decode access token

def decode_access_token(token: str):
    token=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
    return token


# REFRESH TOKEN
def encode_refresh_token(user_id: int):

    now = datetime.datetime.now(datetime.timezone.utc)
    exp = now + datetime.timedelta(days=7)

    payload = {
        "user_id": user_id,
        "token_type": "refresh",
        "iat": now,
        "exp": exp,
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


# DECODE JWT TOKEN
def decode_auth_token(token: str):

    try:
        decoded = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return decoded

    except jwt.ExpiredSignatureError:
        return None

    except jwt.InvalidTokenError:
        return None

# PASSWORD HASH
def hash_password(password: str):
    salt = bcrypt.gensalt()
    pass_hash = bcrypt.hashpw(password.encode("utf-8"), salt)
    return pass_hash.decode("utf-8")


# PASSWORD VERIFY
def verify_password(password: str, hashed_password: str):

    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    except (ValueError, AttributeError):
        return False


# ACTIVATION TOKEN
def generate_activation_token():
    return secrets.token_urlsafe(32)

def generate_refresh_token():
    """
    Generate secure random refresh token.
    """
    return secrets.token_urlsafe(64)

def hash_refresh_token(token: str):
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

def hash_activation_token(token: str):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


# RESET TOKEN
def generate_reset_token():
    return secrets.token_urlsafe(32)

def hash_reset_token(token: str):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def generate_transaction_id():
    return f"TXN-{uuid.uuid4().hex[:20].upper()}"

