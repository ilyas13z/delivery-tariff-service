from fastapi import FastAPI
import uvicorn
from fastapi.routing import APIRouter

from api.handlers import package_router, types_router

#########################
# BLOCK WITH API ROUTES #
#########################

# create instance of the app
app = FastAPI(title="delivery-tariff-service-ilyas13z")

# create the instance for the routes
main_api_router = APIRouter()

# set routes to the app instance
main_api_router.include_router(package_router, prefix="/package", tags=["package"])
app.include_router(main_api_router)

main_api_router.include_router(types_router, prefix="/types", tags=["types"])
app.include_router(main_api_router)


if __name__ == "__main__":
    # run app on the host and port
    uvicorn.run(app, host="0.0.0.0", port=8000)
