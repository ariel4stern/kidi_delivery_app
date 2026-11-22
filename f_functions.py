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
    get_driver,
    get_cartoons_count,
    get_max_cartoons,
    get_available_drivers,
    initial_drivers,
    patch_driver,
    update_driver_to_un_available,

)
from d_dal_points import (
    get_dist_point,
get_all_dist_point
)
from d_dal_points import (
    get_dist_point,
get_all_dist_point
)
from d_router_points import (
    get_points,
    get_point_distributions
)
from e_dal_output_table import (
    patch_output_row, get_current_day,get_all_rows_output,
    get_row_output,insert_row_output,update_output_number
)

from e_router_output_table import (
    PatchOutputData,
    OutputData,
    patch_output_data,
    insert_new_output_row
)

def update_output_table(data_frame: pd.DataFrame)->List[Dict[str,Any]]:
    lst = []
    data_frame = data_frame[['store_numbers','cartoons_count','driver_id']].copy()
    for i in range(len(data_frame)):
        st_number = int(data_frame.loc[i,'store_numbers'])
        st_count = int(data_frame.loc[i,'cartoons_count'])
        driver_id = int(data_frame.loc[i,'driver_id'])


        patched_row = patch_output_row(store_number=st_number,
                         store_count=st_count,
                         driver_id=driver_id)

        if patched_row == 0:
            raise ValueError("parameters provided Wrong.")

        if patched_row == 1:
            raise ValueError("Not such row in output table.")

        if patched_row == 2:
            raise ValueError("Row failed to patch.")

        lst.append(patched_row)

    return lst

def check_for_nan_store(dataframe: pd.DataFrame):
    not_nan_values = dataframe[dataframe['driver_id'].notna()].copy().sort_values(by=['cartoons_count'],ascending=False).reset_index(drop=True)
    nan_values = dataframe[dataframe['driver_id'].isna()].copy().sort_values(by=['cartoons_count'],ascending=False).reset_index(drop=True)
    print(nan_values)
    print(not_nan_values)
    if len(nan_values)==0:
        return None,None
    return nan_values,not_nan_values

def approve_driver_count(d_id:int,count:int,point:float)->bool|None:
    cartoons_count_driver = get_cartoons_count(d_id)
    print("cartoons_count_driver",cartoons_count_driver)
    max_cartoons_per_driver = get_max_cartoons(d_id)
    print("max_cartoons_per_driver",max_cartoons_per_driver)
    print("count",count)
    count=count-1
    if max_cartoons_per_driver is None or cartoons_count_driver is None:
        print(f'approve_driver_count counts is wrong')
        return None

    if max_cartoons_per_driver < (count + cartoons_count_driver):
        print(f"now,:{d_id},{count},{max_cartoons_per_driver}")

        poss_cartoons = max_cartoons_per_driver - cartoons_count_driver
        print("poss_cartoons",poss_cartoons)

        data_output_unuse = OutputData(output_number=point+0.2,
                                 output_count=count-poss_cartoons,
                                 driver_id=5)

        inserted_row = insert_new_output_row(data_output_unuse)
        print(inserted_row)
        patched_driver = patch_driver(
            d_id=d_id,
            d_cartoons_count=poss_cartoons,
            d_name=None, d_phone=None, d_max_cartoons=None, d_distribution_area=None, d_status=None)

        if patched_driver is None:
            print('driver failed to patched')
            raise ValueError('driver failed to patched')

        updated = update_output_number(point,poss_cartoons,d_id)
        print("update_output_number",updated,d_id)
        if updated is None:
            raise ValueError("not such driver")

        update_driver_to_un_available(d_id)
        return True
    else:
        return False

def first_allocation_division_distribution_points(dataframe: pd.DataFrame)->pd.DataFrame|None:
    unfilled_df,filled_df = check_for_nan_store(dataframe)
    if unfilled_df is None:
        return None
    today = str(get_current_day())
    print('today',today)
    for i in unfilled_df.index :

        store_number = int(unfilled_df.loc[i]['store_numbers'])
        store_count = int(unfilled_df.loc[i]['cartoons_count'])
        print(i,store_number)

        point = get_dist_point(today,store_number)
        # {'driver_id': 2, 'driver_name': 'leonid', 'day': 'sunday', 'point': 3}
        if point is None:
            print('not such point today')
            return None

        available_drivers = get_available_drivers()
        print(available_drivers)
        if available_drivers is None:
            print('available drivers not found')
            return None

        driver_id = int(point['driver_id'])
        problem = approve_driver_count(d_id=driver_id,
                             count=store_count,
                             point=store_number)
        print()
        if problem:
            print('approve_driver_count() activated')
            continue

        available_drivers_ids = [d['driver_id'] for d in available_drivers]
        if driver_id not in available_drivers_ids:
            print(f'driver {driver_id} not in available drivers')
            continue



        to_patch = PatchOutputData(output_count=store_count,
                                   driver_id=driver_id)

        patched_row = patch_output_data(output_number=store_number,
                          output_data=to_patch)['updated_row']
        print(patched_row)

        patched_driver = patch_driver(
            d_id=driver_id,
            d_cartoons_count=store_count,
            d_name=None,d_phone=None,d_max_cartoons=None,d_distribution_area=None,d_status=None)

        if patched_driver is None:
            print('driver failed to patched')
            return None

        unfilled_df.loc[i,"driver_id"] = int(patched_row["driver_id"])
        unfilled_df.loc[i,"driver_name"] = str(patched_row["driver_name"])
        print(unfilled_df)


    current_df = pd.concat([filled_df,unfilled_df],ignore_index=True)
    return current_df


df_dict ={'store_numbers': [3,23,30,31],
          'cartoons_count': [120,54,12,72],
          'driver_id': [None,None,None,None],
          'driver_name': [None,None,None,None]}

df = pd.DataFrame(df_dict)

print(first_allocation_division_distribution_points(df))
print(get_dist_point(get_current_day(),3))
print(get_dist_point(get_current_day(),31))

print(get_driver(2))

print(get_available_drivers())

def create_final_file():
    pass

def save_final_file():
    pass