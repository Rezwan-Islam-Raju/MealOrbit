from pydantic import BaseModel, Field


class RiderLocationRequest(BaseModel):
    delivery_id: int
    latitude: float = Field(ge=-90,le=90)
    longitude: float = Field(ge=-180,le=180)


class RiderLocationResponse(BaseModel):
    rider_id: int
    latitude: float
    longitude: float

