import os
from pathlib import Path
from typing import Tuple
import pandas as pd

from c_dal_drivers import (
    get_cartoons_count,
    get_max_cartoons,
    get_available_drivers,
    patch_driver,
    update_driver_count,
    update_driver_available_not
)

from d_dal_points import (
    get_dist_point,
    rows_exists
)

from e_dal_output_table import (
    get_current_day,
    get_all_rows_output,
    update_output_number,
    update_output_count_driver_null,
    clear_output_driver
)

from e_router_output_table import (
    PatchOutputData,
    OutputData,
    patch_output_data,
    insert_new_output_row
)
from eb_router_output_table_two import (
    OutputDataTwo,
    UpdateOutputDataId,
    update_output_data_two_by_number,
    insert_new_output_two_row,
    get_all_rows_output_two

)

BASE_DIR = os.getcwd()
REPORTS_DIR_PATH = Path(BASE_DIR,'distribution_reports')

def counting_confirmation(dataframe: pd.DataFrame):
    for i in dataframe.index:

        store_number = int(dataframe.loc[i,'store_numbers'])
        store_count = int(dataframe.loc[i,'cartoons_count'])

        patched_row = update_output_count_driver_null(st_number=store_number,
                                                      count=store_count)

        if patched_row is None:
            print(f"Not such store number: {store_number}")
            return False

    return True

def convert_output_table_to_df():
    rows = get_all_rows_output()
    if not rows:
        return None

    dataframe = pd.DataFrame(rows)
    return dataframe

def extract_nan_stores(dataframe: pd.DataFrame)-> Tuple[pd.DataFrame | None, pd.DataFrame | None]:
    not_nan_values = dataframe[dataframe['driver_id'].notna()].copy().sort_values(by=['cartoons_count'],ascending=False).reset_index(drop=True)
    nan_values = dataframe[dataframe['driver_id'].isna()].copy().sort_values(by=['cartoons_count'],ascending=False).reset_index(drop=True)
    print(nan_values)
    print(not_nan_values)
    if len(nan_values)==0:
        return None,None
    return nan_values,not_nan_values
def approve_driver_count(d_id:int ,count:int ,point:float) -> bool | None :
    cartoons_count_driver = get_cartoons_count(d_id)

    max_cartoons_per_driver = get_max_cartoons(d_id)
    print("cartoons_count_driver",cartoons_count_driver)
    print("max_cartoons_per_driver",max_cartoons_per_driver)
    if max_cartoons_per_driver is None or cartoons_count_driver is None:
        print('Not such driver')
        return None

    print("condition:",max_cartoons_per_driver < (count + cartoons_count_driver))
    if max_cartoons_per_driver < (count + cartoons_count_driver):
        print("checking_approv")
        poss_cartoons = max_cartoons_per_driver - cartoons_count_driver

        data_output_unuse = OutputDataTwo(output_number=point,
                                       output_count=count - poss_cartoons,
                                       driver_id=None)

        insert_new_output_two_row(data_output_unuse)

        update_driver_count(d_id=d_id,
                     d_cartoons_count=poss_cartoons)

        update_output_number(st_number=point,
                             count=poss_cartoons,
                             d_id=d_id)

        update_driver_available_not(d_id,'un_available')
        return True

    return False

def allocation_division_distribution_points(dataframe: pd.DataFrame) -> pd.DataFrame | None :
    unfilled_df, filled_df = extract_nan_stores(dataframe)
    if unfilled_df is None:
        print('No unfilled data')
        return None

    today = str(get_current_day())

    for i in unfilled_df.index:
        store_number = int(unfilled_df.loc[i]['store_numbers'])
        store_count = int(unfilled_df.loc[i]['cartoons_count'])

        point = get_dist_point(today, store_number)
        if point is None or point['driver_id'] is None:
            print(f'no driver point today for store {store_number}')
            clear_output_driver(store_number, store_count)
            continue

        driver_id = int(point['driver_id'])
        available_ids = [d['driver_id'] for d in (get_available_drivers() or [])]
        print(available_ids)
        if driver_id not in available_ids:          # un_available -> NaN, always
            print(f'driver {driver_id} not in available drivers')
            clear_output_driver(store_number, store_count)
            continue
        approved_driver = approve_driver_count(d_id=driver_id, count=store_count, point=store_number)
        if approved_driver:
            print("approved_driver -- checked")
            continue                                # driver filled up, remainder already NaN

        patched_row = patch_output_data(output_number=store_number,
                                        output_data=PatchOutputData(output_count=store_count,
                                                                    driver_id=driver_id))['updated_row']
        up = update_driver_count(d_id=driver_id, d_cartoons_count=store_count)
        print('up driver:',up)
        unfilled_df.loc[i, "driver_id"] = int(patched_row["driver_id"])
        unfilled_df.loc[i, "driver_name"] = str(patched_row["driver_name"])

    print(pd.concat([filled_df, unfilled_df], ignore_index=True))
    print(convert_output_table_to_df())
    return pd.concat([filled_df, unfilled_df], ignore_index=True)

def merged_output_tables():
    combined = pd.DataFrame(get_all_rows_output())
    if rows_exists("output_data_two"):
        data2 = pd.DataFrame(get_all_rows_output_two())
        combined = pd.concat([combined, data2], ignore_index=True)
    return combined
def export_excel():
    if not REPORTS_DIR_PATH.exists():
        REPORTS_DIR_PATH.mkdir()

    files = [f for f in REPORTS_DIR_PATH.iterdir() if f.is_file()]

    file_number_str = len(files) + 1

    base_file_path = Path(REPORTS_DIR_PATH, f"distribution_report_{file_number_str}.xlsx")

    combined = pd.DataFrame(get_all_rows_output())
    if rows_exists("output_data_two"):
        data2 = pd.DataFrame(get_all_rows_output_two())
        combined = pd.concat([combined, data2], ignore_index=True)

    dataframe = pd.DataFrame(combined)

    dataframe.to_excel(base_file_path, index=False)
    return base_file_path


def print_last_report():
    if not REPORTS_DIR_PATH.exists():
        print("no reports")
        return False

    files = [f for f in REPORTS_DIR_PATH.iterdir() if f.is_file()]

    file_number_str = len(files) + 1
    base_file_path = Path(REPORTS_DIR_PATH, f"distribution_report_{file_number_str}.xlsx")

    os.startfile(base_file_path, "print")
    return True

df_dict ={'store_numbers': [3,23,30,31],
          'cartoons_count': [120,54,12,72],
          'driver_id': [None,None,None,None],
          'driver_name': [None,None,None,None]}

df = pd.DataFrame(df_dict)

# print(first_allocation_division_distribution_points(df))
# print(get_dist_point(get_current_day(),3))
# print(get_dist_point(get_current_day(),31))
# print(get_all_rows_output())
#
# print(get_driver(2))
#
# print(get_available_drivers())
## Physical print file_path
# # # # os.startfile(file_path, "print")