import uuid

from pydantic import BaseModel

#########################
# BLOCK WITH API MODELS #
#########################


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
    price_delivery: float | str


class ShowParcels(TunedModel):
    package_id: uuid.UUID
    name: str
    weight: float
    type_package: int
    price: float
    

class TypePackage(TunedModel):
    type_id: int
    name: str

class CreatePackageResponse(TunedModel):
    package_id: uuid.UUID


class PackageCreate(BaseModel):
    name: str
    weight: float
    type_package: int
    price: float
