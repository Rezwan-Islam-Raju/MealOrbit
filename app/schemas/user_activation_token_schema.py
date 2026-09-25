from pydantic import BaseModel


class UserActivationRequest(BaseModel):
    token: str


class UserActivationResponse(BaseModel):
    message: str