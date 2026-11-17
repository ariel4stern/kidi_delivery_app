from fastapi import FastAPI
from a_dal_stores import initial_stores
from b_dal_delivery import initialize_delivery_table
from c_dal_drivers import initial_drivers
from d_dal_area import initialize_area_distributions
from e_dal_output_table import initialize_output_table

from e_router_output_table import output_router

output_app = FastAPI()

initial_stores()
initialize_delivery_table()
initial_drivers()
initialize_area_distributions()
initialize_output_table()

output_app.include_router(output_router)