from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class ChargingSessionBase(BaseModel):
    user_id: int
    station_id: int
    charger_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    energy_used: float = 0.0
    cost: float = 0.0
    is_active: bool = True


class ChargingSessionCreate(ChargingSessionBase):
    pass


class ChargingSessionUpdate(BaseModel):
    end_time: Optional[datetime] = None
    energy_used: Optional[float] = None
    cost: Optional[float] = None
    is_active: Optional[bool] = None


class ChargingSession(ChargingSessionBase):
    id: int

    class Config:
        orm_mode = True


class StationBase(BaseModel):
    name: str
    location: str
    power_output: float
    ocpp_id: str
    status: str = "Available"
    num_chargers: int = 1
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class StationCreate(StationBase):
    pass


class StationUpdate(BaseModel):
    name: Optional[str]
    location: Optional[str]
    power_output: Optional[float]
    status: Optional[str]
    num_chargers: Optional[int]


class Station(StationBase):
    id: int
    sessions: Optional[List[ChargingSession]] = []  # Nested list of sessions

    class Config:
        orm_mode = True
