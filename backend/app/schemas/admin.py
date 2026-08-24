from pydantic import BaseModel, Field


# -------------------------
# Zone
# -------------------------

class ZoneCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class ZoneUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class ZoneResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


# -------------------------
# Area
# -------------------------

class AreaCreate(BaseModel):
    area_name: str = Field(min_length=1, max_length=150)


class AreaUpdate(BaseModel):
    area_name: str = Field(min_length=1, max_length=150)


class AreaResponse(BaseModel):
    id: int
    zone_id: int
    area_name: str

    class Config:
        from_attributes = True
        
# -------------------------
# Rate Cards
# -------------------------

class RateCardCreate(BaseModel):
    order_type: str
    zone_type: str
    base_rate: float = Field(gt=0)
    additional_rate: float = Field(ge=0)
    weight_limit: float = Field(gt=0)


class RateCardUpdate(BaseModel):
    base_rate: float = Field(gt=0)
    additional_rate: float = Field(ge=0)
    weight_limit: float = Field(gt=0)


class RateCardResponse(BaseModel):
    id: int
    order_type: str
    zone_type: str
    base_rate: float
    additional_rate: float
    weight_limit: float

    class Config:
        from_attributes = True
        
# -------------------------
# COD Charges
# -------------------------

class CodChargeCreate(BaseModel):
    order_type: str
    charge: float = Field(ge=0)


class CodChargeUpdate(BaseModel):
    charge: float = Field(ge=0)


class CodChargeResponse(BaseModel):
    id: int
    order_type: str
    charge: float

    class Config:
        from_attributes = True
        
# -------------------------
# Agents
# -------------------------

class AgentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str
    password: str = Field(min_length=6)
    phone: str | None = None
    zone_id: int | None = None


class AgentZoneUpdate(BaseModel):
    zone_id: int


class AgentResponse(BaseModel):
    id: int
    user_id: int
    zone_id: int | None
    current_latitude: float | None
    current_longitude: float | None
    availability_status: str

    class Config:
        from_attributes = True