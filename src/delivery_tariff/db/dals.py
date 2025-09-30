from typing import Union, List, Set, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_tariff.db.models import Parcels, TypesPackage

###########################################################
# BLOCK FOR INTERACTION WITH DATABASE IN BUSINESS CONTEXT #
###########################################################


class PackageDAL:
    """Data Access Layer for operating user info"""
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_package(
        self, name: str, weight: float, type_id: int, price: int
    ) -> Parcels:
        new_package = Parcels(
            name=name,
            weight=weight,
            type_id=type_id,
            price=price,
        )
        self.db_session.add(new_package)
        await self.db_session.flush()
        return new_package.package_id


    async def get_types_package(self) -> Union[List[TypesPackage], None]:
        query = select(TypesPackage)
        res = await self.db_session.execute(query)
        types = res.scalars().all()
        if types is not None:
            return types
        
    async def get_parcels_by_ids(self, page: int, parcels_id_set: Set[UUID], filter_type_id: Optional[int] = None, filter_price_delivery: Optional[bool] = None) -> List[Parcels]:
        query = select(Parcels).where(Parcels.package_id.in_(parcels_id_set)).options(selectinload(Parcels.type_package))

        if filter_type_id is not None:
            query = query.filter(Parcels.type_id == filter_type_id)

        if filter_price_delivery is not None:
            if filter_price_delivery:
                query = query.filter(Parcels.price_delivery.isnot(None))
            else:
                query = query.filter(Parcels.price_delivery.is_(None))

        offset = (page - 1) * 2
        query = query.offset(offset).limit(2)
        res = await self.db_session.execute(query)
        parcels = res.scalars().all()
        if parcels is not None:
            return parcels

    async def get_package_by_id(self, package_id: UUID) -> Union[Parcels, None]:
        query = select(Parcels).where(Parcels.package_id == package_id).options(selectinload(Parcels.type_package))
        res = await self.db_session.execute(query)
        package_row = res.fetchone()
        if package_row is not None:
            return package_row[0]


class PackageDALSync:
    def __init__(self, db_session):
        self.db_session = db_session
        
    def update_price_delivery(self, exchange_rate: float) -> List[Parcels]:
        query = select(Parcels).filter(Parcels.price_delivery.is_(None))
        res = self.db_session.execute(query)
        parcels = res.scalars().all()
        if parcels is not None:
            for package in parcels:
                # Стоимость = (вес в кг * 0.5 + стоимость содержимого в долларах * 0.01 ) * курс доллара к рублю
                price_delivery = (package.weight * 0.5 + package.price * 0.01) * float(exchange_rate)
                package.price_delivery = round(price_delivery, 2)

            return parcels