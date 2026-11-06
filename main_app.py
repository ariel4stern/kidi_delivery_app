from fastapi import FastAPI
from b_router_delivery import delivery_router
from b_dal_delivery import initialize_delivery_table

delivery_app = FastAPI()

initialize_delivery_table()
delivery_app.include_router(delivery_router)