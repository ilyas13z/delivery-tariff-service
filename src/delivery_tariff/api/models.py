import uuid

from pydantic import BaseModel, field_serializer


class TunedModel(BaseModel):
    class Config:
        """tells pydantic to convert even non dict obj to json"""

        orm_mode = True


class ShowPackage(TunedModel):
    package_id: uuid.UUID
    name: str
    weight: float
    type_package: str
    price: float
    price_delivery: float | None
    
    @field_serializer("price_delivery")
    def serialize_price_delivery(self, value):
        if value is None:
            return "Не рассчитано"
        return value
    

class TypePackage(TunedModel):
    type_id: int
    name: str

class CreatePackageResponse(TunedModel):
    package_id: uuid.UUID


class PackageCreate(BaseModel):
    name: str
    weight: float
    type_id: int
    price: float
