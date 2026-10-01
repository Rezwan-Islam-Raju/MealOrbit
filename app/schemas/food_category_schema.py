from datetime import datetime
from pydantic import BaseModel, Field


# ---------- Request Schemas ----------

class FoodCategoryCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    img_url: str = Field(max_length=500)


class FoodCategoryUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    img_url: str | None = Field(default=None, max_length=500)
    is_active: bool = Field(default=True)



# ---------- Response Schemas ----------

class FoodCategoryResponse(BaseModel):
    id: int
    name: str
    description: str | None
    img_url: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


