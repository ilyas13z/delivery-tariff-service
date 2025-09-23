from typing import Union, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.models import PackageCreate, CreatePackageResponse, ShowPackage, TypePackage, ShowParcels
from db.dals import PackageDAL
from db.session import get_db, redis_client, get_session

package_router = APIRouter()
parcels_router = APIRouter()
types_router = APIRouter()


async def _create_new_package(body: PackageCreate, db, session_id) -> CreatePackageResponse:
    async with db as session:
        async with session.begin():

            package_dal = PackageDAL(session)
            package_id = await package_dal.create_package(
                name=body.name,
                weight=body.weight,
                type_package=body.type_package,
                price=body.price,
            )
            
            key = f"session:{session_id}:parcels"
            await redis_client.sadd(key, str(package_id))
            
            return CreatePackageResponse(
                package_id=package_id,
            )


# async def _delete_user(user_id, db) -> Union[UUID, None]:
#     async with db as session:
#         async with session.begin():
#             user_dal = UserDAL(session)
#             deleted_user_id = await user_dal.delete_user(
#                 user_id=user_id,
#             )
#             return deleted_user_id


# async def _update_user(updated_user_params: dict, user_id: UUID, db) -> Union[UUID, None]:
#     async with db as session:
#         async with session.begin():
#             user_dal = UserDAL(session)
#             updated_user_id = await user_dal.update_user(
#                 user_id=user_id,
#                 **updated_user_params
#             )
#             return updated_user_id


async def _get_package_by_id(package_id, db, session_id) -> Union[ShowPackage, None]:
    async with db as session:
        async with session.begin():
            key = f"session:{session_id}:parcels"
            if not await redis_client.sismember(key, str(package_id)):
                return
            
            package_dal = PackageDAL(session)
            package = await package_dal.get_package_by_id(
                package_id=package_id,
            )
            type_package = await package_dal.get_type_package_by_id(
                type_id=package.type_package,
            )
            if package is not None:
                return ShowPackage(
                    package_id=package.package_id,
                    name=package.name,
                    weight=package.weight,
                    type_package=type_package.name,
                    price=package.price,
                    price_delivery="Не рассчитано",
                )
                
                
async def _get_parcels_by_session_id(db, session_id) -> Union[List[ShowPackage], None]:
    async with db as session:
        async with session.begin():
            package_dal = PackageDAL(session)
            
            key = f"session:{session_id}:parcels"
            parcels_id_set = await redis_client.smembers(key)
            
            parcels = await package_dal.get_parcels_by_ids(
                parcels_id_set=parcels_id_set,
            )
            if parcels is not None:
                return parcels


async def _get_types_package(db) -> Union[List[TypePackage], None]:
    async with db as session:
        async with session.begin():
            package_dal = PackageDAL(session)
            types = await package_dal.get_types_package()
            if types is not None:
                return types


@package_router.post("/", response_model=CreatePackageResponse)
async def create_package(body: PackageCreate, db: AsyncSession = Depends(get_db), session_id = Depends(get_session)) -> CreatePackageResponse:
    return await _create_new_package(body, db, session_id)


# @package_router.delete("/", response_model=DeleteUserResponse)
# async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_db)) -> DeleteUserResponse:
#     deleted_user_id = await _delete_user(user_id, db)
#     if deleted_user_id is None:
#         raise HTTPException(status_code=404, detail=f"User with id {user_id} not found.")
#     return DeleteUserResponse(deleted_user_id=deleted_user_id)


@package_router.get("/", response_model=ShowPackage)
async def get_package_by_id(package_id: UUID, db: AsyncSession = Depends(get_db), session_id = Depends(get_session)) -> ShowPackage:
    package = await _get_package_by_id(package_id, db, session_id)
    if package is None:
        raise HTTPException(status_code=404, detail=f"Package with id = {package_id} not found or this is not your package")
    return package

@parcels_router.get("/", response_model=list[ShowParcels])
async def get_parcels_by_session_id(db: AsyncSession = Depends(get_db), session_id = Depends(get_session)) -> ShowPackage:
    package = await _get_parcels_by_session_id(db, session_id)
    if package is None:
        raise HTTPException(status_code=404, detail="This is not your session id")
    return package


@types_router.get("/", response_model=list[TypePackage])
async def get_types_package(db: AsyncSession = Depends(get_db)) -> TypePackage:
    package = await _get_types_package(db)
    if package is None:
        raise HTTPException(status_code=404, detail="Types of package not found.")
    return package

# @package_router.patch("/", response_model=UpdatedUserResponse)
# async def update_user_by_id(
#         user_id: UUID, body: UpdateUserRequest, db: AsyncSession = Depends(get_db)
# ) -> UpdatedUserResponse:
#     updated_user_params = body.dict(exclude_none=True)
#     if updated_user_params == {}:
#         raise HTTPException(status_code=422, detail="At least one parameter for user update info should be provided")
#     user = await _get_user_by_id(user_id, db)
#     if user is None:
#         raise HTTPException(status_code=404, detail=f"User with id {user_id} not found.")
#     updated_user_id = await _update_user(updated_user_params=updated_user_params, db=db, user_id=user_id)
#     return UpdatedUserResponse(updated_user_id=updated_user_id)
