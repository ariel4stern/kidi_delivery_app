from datetime import datetime
from typing import List, Dict, Any
import numpy as np
import pandas as pd

from a_dal_stores import (
    initial_stores,
    get_stores_area,
    get_store
)
from b_dal_delivery import (
    get_today_store_numbers,
    initialize_delivery_table
)
from c_dal_drivers import (
    get_available_drivers,
    get_cartoons_count,
    initial_drivers,
    patch_driver
)
from c_router_drivers import (
    PatchDriver
)
from d_dal_area import (
    get_dist_point
)


def get_current_day():
    today = datetime.now()

    day_name = today.strftime("%A")

    return day_name.lower()

def prepare_today_distribution_points(today:str) -> None | List[int]  :
    if not today:
        return None
    return get_today_store_numbers(today)['store_numbers']

def find_dedicated_driver(day:str,area:str,count:int) -> List[str] | None :
    drivers = get_available_drivers(count)
    if drivers == 0 :
        raise ValueError('count must be greater than 0')
    if drivers == 1:
        raise ValueError('drivers not found')

    drivers_ids = [driver['driver_id'] for driver in drivers]

    dedicated_drivers_by_area = get_dist_point(day,area)

    if dedicated_drivers_by_area['driver_id'] in drivers_ids:
         return [dedicated_drivers_by_area['driver_name'],dedicated_drivers_by_area['driver_id']]

    return None


def first_allocation_division_distribution_points(dataframe: pd.DataFrame):

    # Extract stores without an assigned driver
    unfilled_df = dataframe[dataframe['driver_id'].isna()].copy()
    print(unfilled_df)
    print(unfilled_df.index)
    print(len(unfilled_df))

    for i in unfilled_df.index:
        store = get_store(unfilled_df.loc[i]['store_number'])
        store_area = str(store['store_area'])
        cartoons_count = int(unfilled_df.loc[i,'cartoons_count'])
        driver = find_dedicated_driver(day=get_current_day(), area=store_area,
                                       count=cartoons_count)
        if driver is None:
            return 'no drivers available'

        unfilled_df.loc[i,'driver_name'] = driver[0]
        unfilled_df.loc[i,'driver_id'] = driver[1]

        patched_driver = patch_driver( int(driver[1]),d_name=None, d_phone=None,
                                  d_cartoons_count=cartoons_count,d_max_cartoons=None,
                                  d_distribution_area=None,d_status=None)

        if patched_driver == 0:
            raise ValueError("no parameter provided")

        if patched_driver == 1:
            raise ValueError("Driver not found")

        if patched_driver == 2:
            raise ValueError("Driver data conflicts with existing data")

    return unfilled_df









initial_stores()
df_dict ={'store_numbers': [1,3,5,9],
          'cartoons_count': [120,54,12,72],
          'driver_id': [1,np.nan,3,4],
          'driver_name': ['leonid',np.nan,'ishai','moshe']}

df = pd.DataFrame(df_dict)

first_allocation_division_distribution_points(df)



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