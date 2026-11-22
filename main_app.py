from fastapi import FastAPI
from a_dal_stores import initialize_stores
from b_dal_delivery import initialize_delivery_table
from c_dal_drivers import initialize_drivers
from d_dal_points import initialize_point_distributions
from e_dal_output_table import initialize_output_table
from d_router_points import point_router

points_app = FastAPI()

initialize_stores()
initialize_delivery_table()
initialize_drivers()
initialize_point_distributions()
initialize_output_table()

points_app.include_router(point_router)