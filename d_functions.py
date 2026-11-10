from datetime import datetime
from typing import List, Dict, Any
import numpy as np
import pandas as pd

from a_dal_stores import (
    initial_stores,
    get_stores_area
)
from b_dal_delivery import (
    get_today_store_numbers,
    initialize_delivery_table
)
from c_dal_drivers import (
    get_available_drivers,
    get_cartoons_count,
    initial_drivers

)


def get_current_day():
    today = datetime.now()

    day_name = today.strftime("%A")

    return day_name.lower()

def prepare_today_distribution_points(today:str) -> None | List[int]  :
    if not today:
        return None
    return get_today_store_numbers(today)['store_numbers']

def find_available_driver() -> List[Dict[str,Any]] | None:
    drivers = get_available_drivers()
    if not drivers:
        return None
    return drivers


def first_allocation_division_distribution_points(dataframe: pd.DataFrame):

    # Extract stores without an assigned driver
    unfilled_df = dataframe[dataframe['driver_id'].isna()].copy()

    # Keep stores that already have an assigned driver
    df_without_nan = dataframe.dropna(subset=['driver_id']).copy()

    # Get available drivers (ids,cartoons_count,driver_name)
    available_drivers_dict = get_available_drivers()

    if not available_drivers_dict:
        return None

    # Iterate over unassigned stores
    for index, store in unfilled_df.iterrows():

        store_cartoon_count = int(store['cartoons_count'])

        # Find a suitable available driver
        for driver_id, driver in available_drivers_dict.items():

            driver_cartoon_count = int(
                driver['cartoons_count']
            )

            if store_cartoon_count <= driver_cartoon_count:

                # Assign driver to store
                unfilled_df.loc[index, 'driver_id'] = driver_id
                unfilled_df.loc[index, 'driver_name'] = driver['driver_name']

                # Remove driver to prevent double assignment
                del available_drivers_dict[driver_id]

                break

initial_stores()
df_dict ={'store_numbers': [1,3,5,9],
          'cartoons_count': [120,54,12,72],
          'driver_name': ['ליאוניד',np.nan,'ישי','משה'],
          'driver_id': [1,np.nan,3,4]}

df = pd.DataFrame(df_dict,index = ['store_numbers'],columns = ['cartoons_count','driver_name'])

print(first_allocation_division_distribution_points(df))



def check_left_distribution_points() -> List[int]:
    pass

def max_problem_allocation_division_distribution_points():
    pass

def area_problem_allocation_division_distribution_points():
    pass

def create_final_file():
    pass

def save_final_file():
    pass