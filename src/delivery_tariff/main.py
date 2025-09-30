from fastapi import FastAPI
import uvicorn
from fastapi.routing import APIRouter

from delivery_tariff.api.handlers import package_router, parcels_router, types_router

app = FastAPI(title="delivery-tariff-service")

main_api_router = APIRouter()

main_api_router.include_router(package_router, prefix="/package", tags=["package"])
app.include_router(main_api_router)

main_api_router.include_router(parcels_router, prefix="/packages", tags=["package"])
app.include_router(main_api_router)

main_api_router.include_router(types_router, prefix="/types", tags=["types"])
app.include_router(main_api_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
