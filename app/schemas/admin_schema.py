from pydantic import BaseModel, ConfigDict


class AdminUserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    role: str
    is_active: bool
    is_verified: bool

