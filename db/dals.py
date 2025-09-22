from typing import Union, List
from uuid import UUID

from sqlalchemy import update, and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Parcels, TypesPackage

###########################################################
# BLOCK FOR INTERACTION WITH DATABASE IN BUSINESS CONTEXT #
###########################################################


class PackageDAL:
    """Data Access Layer for operating user info"""
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_package(
        self, name: str, weight: float, type_package: int, price: int
    ) -> Parcels:
        new_package = Parcels(
            name=name,
            weight=weight,
            type_package=type_package,
            price=price,
        )
        self.db_session.add(new_package)
        await self.db_session.flush()
        return new_package.package_id

    # async def delete_user(self, user_id: UUID) -> Union[UUID, None]:
    #     query = update(User).\
    #         where(and_(User.user_id == user_id, User.is_active == True)).\
    #         values(is_active=False).returning(User.user_id)
    #     res = await self.db_session.execute(query)
    #     deleted_user_id_row = res.fetchone()
    #     if deleted_user_id_row is not None:
    #         return deleted_user_id_row[0]

    # async def get_user_by_id(self, user_id: UUID) -> Union[User, None]:
    #     query = select(User).where(User.user_id == user_id)
    #     res = await self.db_session.execute(query)
    #     user_row = res.fetchone()
    #     if user_row is not None:
    #         return user_row[0]

    async def get_types_package(self) -> Union[List[TypesPackage], None]:
        query = select(TypesPackage)
        res = await self.db_session.execute(query)
        types = res.scalars().all()
        if types is not None:
            return types

    async def get_package_by_id(self, package_id: UUID) -> Union[Parcels, None]:
        query = select(Parcels).where(Parcels.package_id == package_id)
        res = await self.db_session.execute(query)
        package_row = res.fetchone()
        if package_row is not None:
            return package_row[0]

    async def get_type_package_by_id(self, type_id: int) -> Union[TypesPackage, None]:
        query = select(TypesPackage).where(TypesPackage.type_id == type_id)
        res = await self.db_session.execute(query)
        package_row = res.fetchone()
        if package_row is not None:
            return package_row[0]

    # async def get_package_by_session(self, session_id: UUID) -> Union[Parcels, None]:
    #     query = select(Parcels).where(Parcels.session_id == session_id)
    #     res = await self.db_session.execute(query)
    #     package_row = res.fetchone()
    #     if package_row is not None:
    #         return package_row[0]

    # async def update_user(self, user_id: UUID, **kwargs) -> Union[UUID, None]:
    #     query = update(User). \
    #         where(and_(User.user_id == user_id, User.is_active == True)). \
    #         values(kwargs). \
    #         returning(User.user_id)
    #     res = await self.db_session.execute(query)
    #     update_user_id_row = res.fetchone()
    #     if update_user_id_row is not None:
    #         return update_user_id_row[0]
