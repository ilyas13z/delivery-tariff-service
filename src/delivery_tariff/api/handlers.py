from typing import Union, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_tariff.api.models import (
    PackageCreate,
    CreatePackageResponse,
    ShowPackage,
    TypePackage,
)
from delivery_tariff.db.dals import PackageDAL
from delivery_tariff.db.session import get_async_db, redis_client, get_session

package_router = APIRouter()
parcels_router = APIRouter()
types_router = APIRouter()


async def _create_new_package(
    body: PackageCreate, db, session_id
) -> CreatePackageResponse:
    async with db as session:
        async with session.begin():
            package_dal = PackageDAL(session)
            package_id = await package_dal.create_package(
                name=body.name,
                weight=body.weight,
                type_id=body.type_id,
                price=body.price,
            )

            key = f"session:{session_id}:parcels"
            await redis_client.sadd(key, str(package_id))
            await redis_client.expire(key, 3600)

            return CreatePackageResponse(
                package_id=package_id,
            )


async def _get_package_by_id(
    package_id, db, session_id
) -> Union[ShowPackage, None]:
    async with db as session:
        async with session.begin():
            key = f"session:{session_id}:parcels"
            if not await redis_client.sismember(key, str(package_id)):
                return None

            package_dal = PackageDAL(session)
            package = await package_dal.get_package_by_id(
                package_id=package_id,
            )
            if package is not None:
                return ShowPackage(
                    package_id=package.package_id,
                    name=package.name,
                    weight=package.weight,
                    type_package=package.type_package.name,
                    price=package.price,
                    price_delivery=package.price_delivery,
                )
            return None


async def _get_parcels_by_session_id(
    page, filter_type_id, filter_price_delivery, db, session_id
) -> Union[List[ShowPackage], None]:
    async with db as session:
        async with session.begin():
            package_dal = PackageDAL(session)

            key = f"session:{session_id}:parcels"
            parcels_id_set = await redis_client.smembers(key)

            parcels = await package_dal.get_parcels_by_ids(
                parcels_id_set=parcels_id_set,
                filter_price_delivery=filter_price_delivery,
                filter_type_id=filter_type_id,
                page=page,
            )
            if parcels is not None:
                validated_parcels = []
                for package in parcels:
                    validated_parcel = ShowPackage(
                        package_id=package.package_id,
                        name=package.name,
                        weight=package.weight,
                        type_package=package.type_package.name,
                        price=package.price,
                        price_delivery=package.price_delivery,
                    )
                    validated_parcels.append(validated_parcel)
                return validated_parcels
            return None


async def _get_types_package(db) -> Union[List[TypePackage], None]:
    async with db as session:
        async with session.begin():
            package_dal = PackageDAL(session)
            types = await package_dal.get_types_package()
            return types


@package_router.post("/", response_model=CreatePackageResponse)
async def create_package(
    body: PackageCreate,
    db: AsyncSession = Depends(get_async_db),
    session_id=Depends(get_session),
) -> CreatePackageResponse:
    return await _create_new_package(body, db, session_id)


@package_router.get("/", response_model=ShowPackage)
async def get_package_by_id(
    package_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    session_id=Depends(get_session),
) -> ShowPackage:
    package = await _get_package_by_id(package_id, db, session_id)
    if package is None:
        raise HTTPException(
            status_code=404,
            detail=f"Package with id = {package_id} not found or this is not your package",
        )
    return package


@parcels_router.get("/", response_model=list[ShowPackage])
async def get_parcels_by_session_id(
    page: int = 1,
    filter_type_id: Optional[int] = None,
    filter_price_delivery: Optional[bool] = None,
    db: AsyncSession = Depends(get_async_db),
    session_id=Depends(get_session),
) -> ShowPackage:
    package = await _get_parcels_by_session_id(
        page, filter_type_id, filter_price_delivery, db, session_id
    )
    if package is None:
        raise HTTPException(
            status_code=404, detail="This is not your session id"
        )
    return package


@types_router.get("/", response_model=list[TypePackage])
async def get_types_package(
    db: AsyncSession = Depends(get_async_db),
) -> TypePackage:
    package = await _get_types_package(db)
    if package is None:
        raise HTTPException(
            status_code=404, detail="Types of package not found."
        )
    return package
