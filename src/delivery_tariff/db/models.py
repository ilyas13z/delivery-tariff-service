import uuid

from sqlalchemy import Column, String, Integer, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

##############################
# BLOCK WITH DATABASE MODELS #
##############################

Base = declarative_base()


# class User(Base):
#     __tablename__ = "users"

#     user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     name = Column(String, nullable=False)
#     surname = Column(String, nullable=False)
#     email = Column(String, nullable=False, unique=True)
#     is_active = Column(Boolean(), default=True)
    
    
class TypesPackage(Base):
    __tablename__ = "types_package"

    type_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    
    parcels = relationship("Parcels", back_populates="type_package")


class Parcels(Base):
    __tablename__ = "parcels"

    package_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    weight = Column(Float, nullable=False)
    
    type_id = Column(Integer, ForeignKey('types_package.type_id'), nullable=False)
    type_package = relationship("TypesPackage", back_populates="parcels")
    
    price = Column(Float, nullable=False)
    price_delivery = Column(Float, nullable=True)
