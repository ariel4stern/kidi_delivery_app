import os
import pandas as pd
from e_dal_output_table import get_all_rows_output
from pathlib import Path


def convert_sql_to_df():
    rows = get_all_rows_output()
    if not rows:
        return None

    dataframe = pd.DataFrame(rows)
    return dataframe

print(convert_sql_to_df())