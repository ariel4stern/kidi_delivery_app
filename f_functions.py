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
    patch_driver,
    update_driver_to_un_available
)
from d_dal_area import (
    get_dist_point
)
from c_router_drivers import (
    PatchDriver
)





def check_for_nan_store(dataframe: pd.DataFrame):
    not_nan_values = dataframe[dataframe['driver_id'].notna()].copy().sort_values(by=['cartoons_count'],ascending=False).reset_index(drop=True)
    nan_values = dataframe[dataframe['driver_id'].isna()].copy().sort_values(by=['cartoons_count'],ascending=False).reset_index(drop=True)
    if len(nan_values)==0:
        return None
    return nan_values,not_nan_values


def prepare_today_distribution_points(today:str) -> None | List[int]  :
    if not today:
        return None
    return get_today_store_numbers(today)['store_numbers']

def find_dedicated_driver(day:str,area:str,count:int) -> List[str] | int | None :
    drivers = get_available_drivers(count)
    if drivers == 0 :
        print('count must be greater than 0')
        return 0
    if drivers == 1:
        print('drivers not found')
        return 1

    drivers_ids = [driver['driver_id'] for driver in drivers]
    print('drivers_ids ',drivers_ids)
    print('day:',day)
    print('area:',area)
    dedicated_drivers_by_area = get_dist_point(str(day),str(area))
    print('dedicated_drivers_by_area ',dedicated_drivers_by_area)

    if dedicated_drivers_by_area['driver_id'] in drivers_ids:
         return [dedicated_drivers_by_area['driver_name'],dedicated_drivers_by_area['driver_id']]

    return None


def first_allocation_division_distribution_points(dataframe: pd.DataFrame):
    unfilled_df,filled_df = check_for_nan_store(dataframe)
    if unfilled_df is None:
        return None

    for i in unfilled_df.index:
        store = get_store(int(unfilled_df.loc[i]['store_numbers']))
        print(store)
        store_area = str(store['store_area'])
        print(store_area)
        cartoons_count = int(unfilled_df.loc[i,'cartoons_count'])
        print(cartoons_count)
        driver = find_dedicated_driver(day=get_current_day(), area=store_area,
                                       count=cartoons_count)
        print('driver',driver)
        if driver == 0 or driver == 1 or driver is None:
            continue


        patched_driver = patch_driver( int(driver[1]),d_name=None, d_phone=None,
                                  d_cartoons_count=cartoons_count,d_max_cartoons=None,
                                  d_distribution_area=None,d_status=None)

        print(i,patched_driver)

        if patched_driver == 0:
            raise ValueError("no parameter provided")

        if patched_driver == 1:
            print('Driver not found')
            continue

        if patched_driver == 2:
            print(f"{cartoons_count} is too high for {driver[0]} (or any other issue with server)")
            updated_to_un_available = updated_to_un_available(int(driver[1]))
            if updated_to_un_available == 0:
                print('updating driver to un-available went wrong(check for driver_id)')
                return None
            continue

        unfilled_df.loc[i,'driver_name'] = driver[0]
        unfilled_df.loc[i,'driver_id'] = driver[1]

        updated_cartoons_count = int(patched_driver['cartoons_count'])
        print('updated_cartoons_count: ',updated_cartoons_count)
        print(f'current_df:\n\r{unfilled_df}')

    current_df = pd.concat([filled_df,unfilled_df],ignore_index=True)
    return current_df


df_dict ={'store_numbers': [17,26,24,25],
          'cartoons_count': [120,54,12,72],
          'driver_id': [np.nan,np.nan,np.nan,np.nan],
          'driver_name': [np.nan,np.nan,np.nan,np.nan]}

df = pd.DataFrame(df_dict)

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