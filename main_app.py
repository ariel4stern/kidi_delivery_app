from fastapi import FastAPI
from a_dal_stores import initial_stores
from b_dal_delivery import initialize_delivery_table
from c_dal_drivers import initial_drivers
from d_dal_points import initialize_point_distributions
from e_dal_output_table import initialize_output_table
from d_router_points import point_router

points_app = FastAPI()

initial_stores()
initialize_delivery_table()
initial_drivers()
initialize_point_distributions()
initialize_output_table()
points_app.include_router(point_router)