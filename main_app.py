from fastapi import FastAPI
from d_dal_area import initialize_area_distributions
from c_dal_drivers import initial_drivers
from d_router_area import areas_router
areas_app = FastAPI()

initial_drivers()
initialize_area_distributions()
areas_app.include_router(areas_router)