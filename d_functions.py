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


def first_allocation_division_distribution_points(dataframe:pd.DataFrame):
    unfilled_df = dataframe[dataframe.isna().any(axis=1)].copy() #axis = 1 search in df columns its mean row by row ot data
    print(unfilled_df)
    stores_to_fill = unfilled_df['store_numbers']
    return get_stores_area(list(stores_to_fill))

initial_stores()
print(first_allocation_division_distribution_points(pd.DataFrame({'store_numbers': [1,3,5,9],
                                                                  'cartoons_count': [120,None,12,None]})))



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