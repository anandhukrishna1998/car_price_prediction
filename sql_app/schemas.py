from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class VehicleCreate(BaseModel):
    year: int
    km_driven: int
    seats: int
    mileage: float
    engine: int
    max_power: float
    car_company_name: str
    fuel: str
    transmission: str
    owner: str


class car_details(BaseModel):
    timestamp: datetime
    year: int
    km_driven: int
    seats: int
    mileage: float
    engine: int
    max_power: float
    car_company_name: str
    fuel: str
    transmission: str
    owner: str
    predicted_price: float

class Config:
        orm_mode = True
    

