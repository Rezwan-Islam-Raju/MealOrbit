from pydantic import BaseModel


# ---------- Request Schemas ----------

class FoodCreateRequest(BaseModel):
    restaurant_id:int
    category_id:int
    name:str
    description:str
    price:float
    is_available:bool


class FoodUpdateRequest(BaseModel):
    category_id:int
    name:str
    description:str
    price:float



class FoodAvailabilityRequest(BaseModel):
    is_available: bool


# ---------- Response Schemas ----------


class FoodPaginationResponse(BaseModel):
    items:list[FoodResponse]
    total:int
    page:int
    limit:int
    total_pages:int

class FoodResponse(BaseModel):
    id:int
    restaurant_id:int
    category_id:int
    name:str
    description:str
    price:float
    is_available:bool
