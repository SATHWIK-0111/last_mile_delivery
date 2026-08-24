from pydantic import BaseModel, Field
from datetime import datetime

class TrackingEventResponse(BaseModel):
    id: int
    order_id: int
    status: str
    actor_id: int | None
    actor_role: str | None
    remarks: str | None
    timestamp: datetime

    class Config:
        from_attributes = True


class OrderTrackingResponse(BaseModel):
    order_id: int
    current_status: str
    tracking_history: list[TrackingEventResponse]
class OrderStatusUpdateRequest(BaseModel):
    status: str

class OrderCalculateRequest(BaseModel):

    pickup_address: str = Field(
        min_length=3
    )

    drop_address: str = Field(
        min_length=3
    )

    length: float = Field(
        gt=0
    )

    breadth: float = Field(
        gt=0
    )

    height: float = Field(
        gt=0
    )

    actual_weight: float = Field(
        gt=0
    )

    order_type: str

    payment_type: str


class OrderCalculateResponse(BaseModel):

    pickup_zone_id: int
    pickup_zone: str

    drop_zone_id: int
    drop_zone: str

    zone_type: str

    actual_weight: float
    volumetric_weight: float
    billable_weight: float

    order_type: str
    payment_type: str

    rate_card_id: int

    base_charge: float
    cod_charge: float
    total_charge: float
    
class OrderCreateRequest(BaseModel):

    pickup_address: str = Field(
        min_length=3
    )

    drop_address: str = Field(
        min_length=3
    )

    length: float = Field(
        gt=0
    )

    breadth: float = Field(
        gt=0
    )

    height: float = Field(
        gt=0
    )

    actual_weight: float = Field(
        gt=0
    )
    pickup_latitude: float | None = None
    pickup_longitude: float | None = None
    order_type: str

    payment_type: str
    
class OrderResponse(BaseModel):

    id: int
    customer_id: int

    pickup_address: str
    drop_address: str

    pickup_zone_id: int
    drop_zone_id: int

    length: float
    breadth: float
    height: float

    actual_weight: float
    volumetric_weight: float
    billable_weight: float

    order_type: str
    payment_type: str

    base_charge: float
    cod_charge: float
    total_charge: float

    current_status: str

    class Config:
        from_attributes = True