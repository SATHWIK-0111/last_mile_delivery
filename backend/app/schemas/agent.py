from pydantic import BaseModel


class AvailabilityUpdate(BaseModel):
    status: str