# Import required libraries
import pandas as pd
import numpy as np
import os
import datetime
# import dash_html_components as html
from dash import html
from dash import html, callback, Input, Output
import plotly.express as px
from dash import dash_table
import plotly.graph_objs as go
import warnings
import re
from Summary_table import table_summary
# from sqlalchemy import create_engine
import sqlite3
from functools import lru_cache
# from app import df_raw, df_mcm, df_card, df_smr
warnings.simplefilter(action='ignore', category=UserWarning)
pd.options.mode.chained_assignment = None

basedir = os.path.abspath(os.path.dirname(__file__))

# sql_data.cache_clear()


def alpha_num_order(string):
    return ''.join([format(int(x), '05d') if x.isdigit()
                    else x for x in re.split(r'(\d+)', string)])


# engine = create_engine("mysql+pymysql://root:sep_2022@localhost/tarundb")
# df_raw = pd.read_sql('SELECT * FROM Faults_data', engine)  # read the entire table
# df_card = pd.read_sql('SELECT * FROM Card_data', engine)
# df_smr = pd.read_sql('SELECT * FROM SMR_data', engine)
# df_mcm = pd.read_sql('SELECT * FROM MCM_data', engine)

# SQLITE_DB_DIR = os.path.join(basedir, "../sql_data")
# engine = "sqlite:///" + os.path.join(SQLITE_DB_DIR, "adc.sqlite3")  # adc.sqlite3
engine1 = sqlite3.connect('sql_data/ALL_FAULTS_WITH_JUNE.sqlite3')

df_raw = pd.read_sql_query('SELECT * FROM RAW', engine1)  # read the entire table
df_card = pd.read_sql_query('SELECT * FROM Card', engine1)
df_smr = pd.read_sql_query('SELECT * FROM SMR', engine1)
df_mcm = pd.read_sql_query('SELECT * FROM MCM', engine1)


def month_data(df_card_data):
    months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    df_month = df_card_data['MONTH'].unique()
    sorted(df_month, key=lambda x: months.index(x.split(",")[0]))
    final_month_list = sorted(df_month, key=lambda x: (int(x.split(",")[1]), months.index(x.split(",")[0])))

    return final_month_list


df = df_raw[['PRODUCT_NAME', 'PART_CODE', 'DATE', 'MONTH', 'STAGE', 'FAULT_OBSERVED', 'FAULT_CATEGORY',
             'REPAIRING_ACTION', 'KEY_COMPONENT', 'POSSIBLE_REASON']]
#
# # group by product for card
# card_product_total = df_card.groupby(['PRODUCT'])[['TEST_QUANTITY', 'PASS_QUANTITY', 'REJECT_QUANTITY',
# 'FTY_PERCENT']]
# .sum()
# # group by product for part code and month
# card_part_code_month = df_card.groupby(['PRODUCT', 'PART_CODE', 'MONTH'])[['TEST_QUANTITY', 'PASS_QUANTITY',
#                                                                            'REJECT_QUANTITY', 'FTY_PERCENT']]\
#     .sum().reset_index()
#
# # group by product for month
# card_month = df_card.groupby(['PRODUCT', 'MONTH'])[['TEST_QUANTITY', 'PASS_QUANTITY', 'REJECT_QUANTITY',
# 'FTY_PERCENT']]\
#     .sum().reset_index().set_index('PRODUCT')
#
# # df_smr = sheet_to_df_map.get("SMR")
# df_smr_filter = df_smr.groupby('PRODUCT').sum()
# df_smr_month = df_smr.groupby(['PRODUCT', 'MONTH']).sum().reset_index().set_index('PRODUCT')
# df_smr_part_no = df_smr.groupby(['PRODUCT', 'MONTH', 'PART_CODE']).sum().reset_index().set_index('PRODUCT')
# # df_mcm = sheet_to_df_map.get("MCM")
# df_mcm_filter = df_mcm.groupby('PRODUCT').sum()
# df_mcm_month = df_mcm.groupby(['PRODUCT', 'MONTH']).sum().reset_index().set_index('PRODUCT')
# df_mcm_part_no = df_mcm.groupby(['PRODUCT', 'MONTH', 'PART_CODE']).sum().reset_index().set_index('PRODUCT')


# def modify_remarks(merged_df, df_pending_date):
#     print(merged_df)
#     # if merged_df["FAULT_CATEGORY"] == "Pending":
#     if "PENDING" in merged_df["FAULT_CATEGORY"]:
#         df_date = df_pending_date[df_pending_date["FAULT_OBSERVED"] == merged_df["FAULT_OBSERVED"]]
#         return "Pending" + "(" + str(merged_df["PENDING"]) + ")" + " since " + str(df_date["DATE"].max())
#     # if merged_df["FAULT_CATEGORY"] == "RETEST":
#     if "Retest" in merged_df["FAULT_CATEGORY"]:
#         return "Retest" + "(" + str(merged_df["Retest"]) + ")"
#
#     else:
#         return merged_df["FAULT_CATEGORY"] + "(" + merged_df["KEY_COMPONENT"] + ")"


def remarks(data):
    # df_raw1 = pd.read_sql('SELECT * FROM Faults_data', engine)  # read the entire table
    df_raw1 = data
    df_raw1 = df_raw1.replace({"COMPONENT DAMAGE": "Dmg",
                               "COMPONENT MISSING": "Miss",
                               "Component faulty": "faulty",
                               "REVERSE POLARITY": "Polarity",
                               "SOLDERING ISSUE": "Solder", "DRY SOLDER": "Dry Solder", "SCRAP": "Scrap",
                               "MAGNETICS ISSUE": "Magnetics",
                               "COMPONENT FAIL ISSUE": "Comp. Fail",
                               "COMPONENT DAMAGE/MISS ISSUE": "Comp. Dmg/Miss", "PENDING": "Pending",
                               "WRONG MOUNT": "Wrong Mount", "CC ISSUE": "CC Issue", "RETEST": "Retest"})

    category = pd.crosstab(df_raw1["FAULT_OBSERVED"], df_raw1["FAULT_CATEGORY"])
    df_pending_date = df_raw1[['FAULT_OBSERVED', 'DATE', 'FAULT_CATEGORY']]
    df_pending_date = df_pending_date[df_pending_date["FAULT_CATEGORY"] == "Pending"]

    category1_df = pd.DataFrame(category)
    df_remarks = df_raw1.pivot_table(index=["FAULT_OBSERVED", "FAULT_CATEGORY"], values='KEY_COMPONENT',
                                     aggfunc=lambda x: ", ".join(str(v) for v in x.unique())).fillna('').reset_index()

    # TO GET PENDING QUANTITY
    for i in range(len(df_remarks)):
        cell_value = df_remarks.iloc[i]['KEY_COMPONENT']
        cell_value = cell_value.split(",")
        key_list = [s.strip(',') for s in cell_value]
        key_list.sort(key=alpha_num_order)
        df_remarks.at[i, 'KEY_COMPONENT'] = ",".join(list(set(key_list)))

        df_remarks["REMARKS"] = df_remarks.apply(
            lambda row: "{}({})".format(row["FAULT_CATEGORY"], str(row["KEY_COMPONENT"])), axis=1)

    lis_col_names = list(category1_df.columns.values)
    lis_col_names_all = ["CC ISSUE", "COMPONENT FAIL ISSUE", "COMPONENT DAMAGE/MISS ISSUE", "MAGNETICS ISSUE",
                         "DRY SOLDER", "SCRAP", "SOLDERING ISSUE", "WRONG MOUNT", "REVERSE POLARITY", "PENDING",
                         "UNDER ANALYSIS", "RETEST", "Polarity", "Solder", "Dry Solder", "Scrap", "Magnetics",
                         "Comp. Fail", "Comp. Dmg/Miss", "Pending", "Wrong Mount", "CC Issue", "Retest"]
    for i in lis_col_names_all:
        if i not in lis_col_names:
            category1_df[i] = 0
    category1_df.reset_index()
    merged_df = pd.merge(df_remarks, category1_df["Pending"], on="FAULT_OBSERVED")
    merged_df = pd.merge(merged_df, category1_df["Retest"], on="FAULT_OBSERVED")
    df_pending_date['DATE'] = pd.to_datetime(df_pending_date['DATE']).dt.date

    def modify_remarks(row):
        # print(row)
        if row["FAULT_CATEGORY"] == "Pending":
            df_date = df_pending_date[df_pending_date["FAULT_OBSERVED"] == row["FAULT_OBSERVED"]]
            # print(row["PENDING"])
            # print(df_pending_date)
            return "Pending" + "(" + str(row["Pending"]) + ")" + " since " + str(df_date["DATE"].max())
        if row["FAULT_CATEGORY"] == "Retest":
            # print(row["Retest"])
            return "Retest" + "(" + str(row["Retest"]) + ")"

        else:
            return row["FAULT_CATEGORY"] + "(" + row["KEY_COMPONENT"] + ")"

    merged_df["REMARKS"] = merged_df.apply(modify_remarks, axis=1)

    # merged_df["REMARKS"] = merged_df.apply(modify_remarks, axis=1)
    # merged_df["REMARKS"] = modify_remarks(merged_df, df_pending_date)
    # Group by FAULT_OBSERVED and aggregate the REMARKS column
    df_remarks = merged_df.groupby("FAULT_OBSERVED").agg(REMARKS=('REMARKS', ', '.join)).reset_index()
    # print(df_remarks)
    return df_remarks


@lru_cache(maxsize=128)  # Set the maximum cache size
def sql_data(dataframe):
    modules_f2 = ['2KW SMR', '3KW SMR', '4KW SMR', 'SMR_2KW_SOLAR', 'SMR_3KW_SOLAR', 'CHARGER', 'M1000', 'M2000',
                  'WCBMS', '2KW SUN MOBILITY', 'SMR_1.1KW', 'CHARGER_1.1KW', 'DCIO_F2']
    engine = sqlite3.connect('sql_data/ALL_FAULTS_WITH_JUNE.sqlite3')
    df_raw1 = pd.read_sql('SELECT * FROM RAW', engine)  # read the entire table
    df_card1 = pd.read_sql('SELECT * FROM Card', engine)
    df_smr1 = pd.read_sql('SELECT * FROM SMR', engine)
    df_mcm1 = pd.read_sql('SELECT * FROM MCM', engine)

    # df_raw1 = pd.read_sql('SELECT * FROM Faults_data', engine)  # read the entire table
    df_raw1_f1 = df_raw1.loc[~df_raw1['PRODUCT_NAME'].isin(modules_f2)]
    df_raw1_f2 = df_raw1.loc[df_raw1['PRODUCT_NAME'].isin(modules_f2)]

    # df_card1 = pd.read_sql('SELECT * FROM Card_data', engine)
    df_card1_f1 = df_card1.loc[~df_card1['PRODUCT'].isin(modules_f2)]
    df_card1_f2 = df_card1.loc[df_card1['PRODUCT'].isin(modules_f2)]
    # df_smr1 = pd.read_sql('SELECT * FROM SMR_data', engine)
    # df_mcm1 = pd.read_sql('SELECT * FROM MCM_data', engine)
    f1_data = df_card1.loc[~df_card1['PRODUCT'].isin(modules_f2)]
    f2_data = df_card1.loc[df_card1['PRODUCT'].isin(modules_f2)]

    card_product_total = df_card1.groupby(['PRODUCT'])[
        ['TEST_QUANTITY', 'PASS_QUANTITY', 'REJECT_QUANTITY', 'FTY_PERCENT']].sum()
    card_product_total_f1 = f1_data.groupby(['PRODUCT'])[
        ['TEST_QUANTITY', 'PASS_QUANTITY', 'REJECT_QUANTITY', 'FTY_PERCENT']].sum()
    card_product_total_f2 = f2_data.groupby(['PRODUCT'])[
        ['TEST_QUANTITY', 'PASS_QUANTITY', 'REJECT_QUANTITY', 'FTY_PERCENT']].sum()

    card_part_code_month = df_card1.groupby(['PRODUCT', 'PART_CODE', 'MONTH'])[['TEST_QUANTITY', 'PASS_QUANTITY',
                                                                               'REJECT_QUANTITY', 'FTY_PERCENT']] \
        .sum().reset_index()
    card_part_code_month_f1 = f1_data.groupby(['PRODUCT', 'PART_CODE', 'MONTH'])[['TEST_QUANTITY', 'PASS_QUANTITY',
                                                                                  'REJECT_QUANTITY', 'FTY_PERCENT']] \
        .sum().reset_index()
    card_part_code_month_f2 = f2_data.groupby(['PRODUCT', 'PART_CODE', 'MONTH'])[['TEST_QUANTITY', 'PASS_QUANTITY',
                                                                                 'REJECT_QUANTITY', 'FTY_PERCENT']] \
        .sum().reset_index()

    card_month = df_card1.groupby(['PRODUCT', 'MONTH'])[['TEST_QUANTITY', 'PASS_QUANTITY', 'REJECT_QUANTITY',
                                                         'FTY_PERCENT']].sum().reset_index().set_index('PRODUCT')
    card_month_f1 = f1_data.groupby(['PRODUCT', 'MONTH'])[['TEST_QUANTITY', 'PASS_QUANTITY', 'REJECT_QUANTITY',
                                                           'FTY_PERCENT']].sum().reset_index().set_index('PRODUCT')
    card_month_f2 = f2_data.groupby(['PRODUCT', 'MONTH'])[['TEST_QUANTITY', 'PASS_QUANTITY', 'REJECT_QUANTITY',
                                                          'FTY_PERCENT']].sum().reset_index().set_index('PRODUCT')
    df_smr_filter = df_smr1.groupby('PRODUCT').sum()
    df_smr_month = df_smr1.groupby(['PRODUCT', 'MONTH']).sum().reset_index().set_index('PRODUCT')
    df_smr_part_no = df_smr1.groupby(['PRODUCT', 'MONTH', 'PART_CODE']).sum().reset_index().set_index('PRODUCT')
    df_mcm_filter = df_mcm1.groupby('PRODUCT').sum()
    df_mcm_month = df_mcm1.groupby(['PRODUCT', 'MONTH']).sum().reset_index().set_index('PRODUCT')
    df_mcm_part_no = df_mcm1.groupby(['PRODUCT', 'MONTH', 'PART_CODE']).sum().reset_index().set_index('PRODUCT')

    if dataframe == "raw":
        data = df_raw1
        return data
    elif dataframe == "raw_f1":
        data = df_raw1_f1
        return data
    elif dataframe == "raw_f2":
        data = df_raw1_f2
        return data
    elif dataframe == "card":
        data = df_card1
        return data
    elif dataframe == "card_f1":
        data = df_card1_f1
        return data
    elif dataframe == "card_f2":
        data = df_card1_f2
        return data
    elif dataframe == "smr":
        data = df_smr1
        return data
    elif dataframe == "mcm":
        data = df_mcm1
        return data
    elif dataframe == "card_total":
        data = card_product_total
        return data
    elif dataframe == "card_total_f1":
        data = card_product_total_f1
        return data
    elif dataframe == "card_total_f2":
        data = card_product_total_f2
        return data
    elif dataframe == "card_part":
        data = card_part_code_month
        return data
    elif dataframe == "card_part_f1":
        data = card_part_code_month_f1
        return data
    elif dataframe == "card_part_f2":
        data = card_part_code_month_f2
        return data
    elif dataframe == "card_month":
        data = card_month
        return data
    elif dataframe == "card_month_f1":
        data = card_month_f1
        return data
    elif dataframe == "card_month_f2":
        data = card_month_f2
        return data
    elif dataframe == "smr_total":
        data = df_smr_filter
        return data
    elif dataframe == "smr_month":
        data = df_smr_month
        return data
    elif dataframe == "smr_part":
        data = df_smr_part_no
        return data
    elif dataframe == "mcm_total":
        data = df_mcm_filter
        return data
    elif dataframe == "smr_month":
        data = df_mcm_month
        return data
    elif dataframe == "mcm_part":
        data = df_mcm_part_no
        return data


def colour_condition(a):
    df_colour = a
    column_name = df_colour.columns
    size = len(column_name)
    # print(column_name)

    # if 'id' in df_colour:
    #     df_numeric_columns = df_colour.select_dtypes('number').drop(['id'], axis=1)
    # else:
    #     df_numeric_columns = df_colour.select_dtypes('number')
    # styles = []

    if size == 6:
        column_1 = column_name[2]
        column_2 = column_name[4]
        return [
            {
                'if': {
                    'filter_query': '{{{column1}}} > {{{column2}}}'.format(column1=column_1, column2=column_2),
                    'column_id': column_2
                },
                'backgroundColor': '#3D9970',
                'color': 'white'
            }, {
                'if': {
                    'filter_query': '{{{column1}}} < {{{column2}}}'.format(column1=column_1, column2=column_2),
                    'column_id': column_2
                },
                'backgroundColor': 'tomato',
                'color': 'white'
            }
        ]


colors = {
    # For black backgroung
    # 'background': 'rgb(50, 50, 50)',
    # 'text':  'white'      # '#7FDBFF'
    'background': 'white',
    'text':  'black'      # '#7FDBFF'
}


# TASK 2:
# Add a callback function for `Products` as input, `Faults` as output


@callback(
    Output('navbar-output', 'children'),
    [Input('navbar-button', 'n_clicks')]
)
def clear_cache(n_clicks):
    if n_clicks is not None:
        sql_data.cache_clear()
        print("Cache cleared.")
        # return "Cache cleared."
        return


@callback(
    [Output(component_id='tested_value', component_property='children'),
     Output(component_id='pass_value', component_property='children'),
     Output(component_id='fail_value', component_property='children'),
     Output(component_id='fty_value', component_property='children'),
     Output(component_id='dpt_value', component_property='children')],
    [Input(component_id='Products', component_property='value'),
     Input(component_id='Part_no', component_property='value'),
     Input(component_id='Month', component_property='value'),
     # Input(component_id='interval_db', component_property='n_intervals')
     ])
def test_count(product, part_no, month):
    total = sql_data("card_total")  # for total
    month_wise = sql_data("card_month")  # month vise card
    part_code_wise = sql_data("card_part")  # for part code data

    if product is None:
        if month is None or len(month) == 0:
            if part_no == 'all_values':
                tested_value = total['TEST_QUANTITY'].sum()
                pass_value = total['PASS_QUANTITY'].sum()
                fail_value = total['REJECT_QUANTITY'].sum()
                fty_value = str(round(((pass_value / tested_value) * 100), 1)) + '%'
                dpt_value = str(int(round(((fail_value / tested_value) * 1000), 0)))
                # return tested_value, pass_value, fail_value, fty_value
            else:
                tested_value = part_code_wise.loc[part_code_wise['PART_CODE'] == part_no]['TEST_QUANTITY'].sum()
                pass_value = part_code_wise.loc[part_code_wise['PART_CODE'] == part_no]['PASS_QUANTITY'].sum()
                fail_value = part_code_wise.loc[part_code_wise['PART_CODE'] == part_no]['REJECT_QUANTITY'].sum()
                fty_value = str(round(((pass_value / tested_value) * 100), 1)) + '%'
                dpt_value = str(int(round(((fail_value / tested_value) * 1000), 0)))
                # return tested_value, pass_value, fail_value, fty_value
        else:
            # print("month is not none")
            # print(len(month))
            if part_no == 'all_values':
                tested_value = month_wise.loc[month_wise['MONTH'].isin(month)]['TEST_QUANTITY'].sum()
                pass_value = month_wise.loc[month_wise['MONTH'].isin(month)]['PASS_QUANTITY'].sum()
                fail_value = month_wise.loc[month_wise['MONTH'].isin(month)]['REJECT_QUANTITY'].sum()
                fty_value = str(round(((pass_value / tested_value) * 100), 1)) + '%'
                dpt_value = str(int(round(((fail_value / tested_value) * 1000), 0)))
                # return tested_value, pass_value, fail_value, fty_value
            else:
                specific = part_code_wise.loc[part_code_wise['MONTH'].isin(month)]
                tested_value = specific.loc[specific['PART_CODE'] == part_no]['TEST_QUANTITY'].sum()
                pass_value = specific.loc[specific['PART_CODE'] == part_no]['PASS_QUANTITY'].sum()
                fail_value = specific.loc[specific['PART_CODE'] == part_no]['REJECT_QUANTITY'].sum()
                fty_value = str(round(((pass_value / tested_value) * 100), 1)) + '%'
                dpt_value = str(int(round(((fail_value / tested_value) * 1000), 0)))
                # return tested_value, pass_value, fail_value, fty_value
    else:
        if month is None or len(month) == 0:
            if part_no == 'all_values':
                tested_value = total['TEST_QUANTITY'].loc[product]
                pass_value = total['PASS_QUANTITY'].loc[product]
                fail_value = total['REJECT_QUANTITY'].loc[product]
                fty_value = str(round(((pass_value / tested_value) * 100), 1)) + '%'
                dpt_value = str(int(round(((fail_value / tested_value) * 1000), 0)))
                # return tested_value, pass_value, fail_value, fty_value
            else:
                specific = part_code_wise.loc[part_code_wise['PRODUCT'] == product]
                tested_value = specific.loc[specific['PART_CODE'] == part_no]['TEST_QUANTITY'].sum()
                pass_value = specific.loc[specific['PART_CODE'] == part_no]['PASS_QUANTITY'].sum()
                fail_value = specific.loc[specific['PART_CODE'] == part_no]['REJECT_QUANTITY'].sum()
                fty_value = str(round(((pass_value / tested_value) * 100), 1)) + '%'
                dpt_value = str(int(round(((fail_value / tested_value) * 1000), 0)))
                # return tested_value, pass_value, fail_value, fty_value
        else:
            month_check = month_wise.loc[month_wise['MONTH'].isin(month)]
            if product in month_check["TEST_QUANTITY"]:
                if part_no == 'all_values':
                    a = month_wise.loc[month_wise['MONTH'].isin(month)]
                    # print(a)
                    tested_value = a['TEST_QUANTITY'].loc[product].sum()
                    pass_value = a['PASS_QUANTITY'].loc[product].sum()
                    fail_value = a['REJECT_QUANTITY'].loc[product].sum()
                    fty_value = str(round(((pass_value / tested_value) * 100), 1)) + '%'
                    dpt_value = str(int(round(((fail_value / tested_value) * 1000), 0)))
                    # return tested_value, pass_value, fail_value, fty_value
                else:
                    specific = part_code_wise.loc[part_code_wise['PRODUCT'] == product]
                    filtered = specific.loc[specific['MONTH'].isin(month)]
                    tested_value = filtered.loc[filtered['PART_CODE'] == part_no]['TEST_QUANTITY'].sum()
                    pass_value = filtered.loc[filtered['PART_CODE'] == part_no]['PASS_QUANTITY'].sum()
                    fail_value = filtered.loc[filtered['PART_CODE'] == part_no]['REJECT_QUANTITY'].sum()
                    fty_value = str(round(((pass_value / tested_value) * 100), 1)) + '%'
                    dpt_value = str(int(round(((fail_value / tested_value) * 1000), 0)))
                    # return tested_value, pass_value, fail_value, fty_value
            else:
                tested_value = 0
                pass_value = 0
                fail_value = 0
                fty_value = 0
                dpt_value = 0

    return tested_value, pass_value, fail_value, fty_value, dpt_value


@callback(Output(component_id='fty_value', component_property='style'),
          Input(component_id='fty_value', component_property='children'))
def fty_style(fty_value):
    if fty_value is not None:
        fty_val = fty_value.replace('%', '')
        value = float(fty_val)
        # print(value)
        if value >= 98:
            return {
                'textAlign': 'center',
                'color': 'lime', 'margin-top': '-18px',
                'fontSize': 40
            }
        else:
            return {
                'textAlign': 'center',
                'color': 'red', 'margin-top': '-18px',
                'fontSize': 40
            }
    # print(fty_value)
    # print(type(fty_value))
    return {
        'textAlign': 'center',
        'color': 'red', 'margin-top': '-18px',
        'fontSize': 40
    }


@callback(
    [Output(component_id='tested_value_f2', component_property='children'),
     Output(component_id='pass_value_f2', component_property='children'),
     Output(component_id='fail_value_f2', component_property='children'),
     Output(component_id='fty_value_f2', component_property='children'),
     Output(component_id='dpt_value_f2', component_property='children')],
    [Input(component_id='Product_f2', component_property='value'),
     Input(component_id='Part_no_f2', component_property='value'),
     Input(component_id='Month_f2', component_property='value'),
     # Input(component_id='interval_db', component_property='n_intervals')
     ])
def test_count(product, part_no, month):
    total = sql_data("card_total_f2")  # for total
    month_wise = sql_data("card_month_f2")  # month vise card
    part_code_wise = sql_data("card_part_f2")  # for part code data

    if product is None:
        if month is None or len(month) == 0:
            if part_no == 'all_values':
                tested_value = total['TEST_QUANTITY'].sum()
                pass_value = total['PASS_QUANTITY'].sum()
                fail_value = total['REJECT_QUANTITY'].sum()
                fty_value = str(round(((pass_value / tested_value) * 100), 1)) + '%'
                dpt_value = str(int(round(((fail_value / tested_value) * 1000), 0)))
                # return tested_value, pass_value, fail_value, fty_value
            else:
                tested_value = part_code_wise.loc[part_code_wise['PART_CODE'] == part_no]['TEST_QUANTITY'].sum()
                pass_value = part_code_wise.loc[part_code_wise['PART_CODE'] == part_no]['PASS_QUANTITY'].sum()
                fail_value = part_code_wise.loc[part_code_wise['PART_CODE'] == part_no]['REJECT_QUANTITY'].sum()
                fty_value = str(round(((pass_value / tested_value) * 100), 1)) + '%'
                dpt_value = str(int(round(((fail_value / tested_value) * 1000), 0)))
                # return tested_value, pass_value, fail_value, fty_value
        else:
            # print("month is not none")
            # print(len(month))
            if part_no == 'all_values':
                tested_value = month_wise.loc[month_wise['MONTH'].isin(month)]['TEST_QUANTITY'].sum()
                pass_value = month_wise.loc[month_wise['MONTH'].isin(month)]['PASS_QUANTITY'].sum()
                fail_value = month_wise.loc[month_wise['MONTH'].isin(month)]['REJECT_QUANTITY'].sum()
                fty_value = str(round(((pass_value / tested_value) * 100), 1)) + '%'
                dpt_value = str(int(round(((fail_value / tested_value) * 1000), 0)))
                # return tested_value, pass_value, fail_value, fty_value
            else:
                specific = part_code_wise.loc[part_code_wise['MONTH'].isin(month)]
                tested_value = specific.loc[specific['PART_CODE'] == part_no]['TEST_QUANTITY'].sum()
                pass_value = specific.loc[specific['PART_CODE'] == part_no]['PASS_QUANTITY'].sum()
                fail_value = specific.loc[specific['PART_CODE'] == part_no]['REJECT_QUANTITY'].sum()
                fty_value = str(round(((pass_value / tested_value) * 100), 1)) + '%'
                dpt_value = str(int(round(((fail_value / tested_value) * 1000), 0)))
                # return tested_value, pass_value, fail_value, fty_value
    else:
        if month is None or len(month) == 0:
            if part_no == 'all_values':
                tested_value = total['TEST_QUANTITY'].loc[product]
                pass_value = total['PASS_QUANTITY'].loc[product]
                fail_value = total['REJECT_QUANTITY'].loc[product]
                fty_value = str(round(((pass_value / tested_value) * 100), 1)) + '%'
                dpt_value = str(int(round(((fail_value / tested_value) * 1000), 0)))
                # return tested_value, pass_value, fail_value, fty_value
            else:
                specific = part_code_wise.loc[part_code_wise['PRODUCT'] == product]
                tested_value = specific.loc[specific['PART_CODE'] == part_no]['TEST_QUANTITY'].sum()
                pass_value = specific.loc[specific['PART_CODE'] == part_no]['PASS_QUANTITY'].sum()
                fail_value = specific.loc[specific['PART_CODE'] == part_no]['REJECT_QUANTITY'].sum()
                fty_value = str(round(((pass_value / tested_value) * 100), 1)) + '%'
                dpt_value = str(int(round(((fail_value / tested_value) * 1000), 0)))
                # return tested_value, pass_value, fail_value, fty_value
        else:
            month_check = month_wise.loc[month_wise['MONTH'].isin(month)]
            if product in month_check["TEST_QUANTITY"]:
                if part_no == 'all_values':
                    a = month_wise.loc[month_wise['MONTH'].isin(month)]
                    tested_value = a['TEST_QUANTITY'].loc[product].sum()
                    pass_value = a['PASS_QUANTITY'].loc[product].sum()
                    fail_value = a['REJECT_QUANTITY'].loc[product].sum()
                    fty_value = str(round(((pass_value / tested_value) * 100), 1)) + '%'
                    dpt_value = str(int(round(((fail_value / tested_value) * 1000), 0)))
                    # return tested_value, pass_value, fail_value, fty_value
                else:
                    specific = part_code_wise.loc[part_code_wise['PRODUCT'] == product]
                    filtered = specific.loc[specific['MONTH'].isin(month)]
                    tested_value = filtered.loc[filtered['PART_CODE'] == part_no]['TEST_QUANTITY'].sum()
                    pass_value = filtered.loc[filtered['PART_CODE'] == part_no]['PASS_QUANTITY'].sum()
                    fail_value = filtered.loc[filtered['PART_CODE'] == part_no]['REJECT_QUANTITY'].sum()
                    fty_value = str(round(((pass_value / tested_value) * 100), 1)) + '%'
                    dpt_value = str(int(round(((fail_value / tested_value) * 1000), 0)))
                    # return tested_value, pass_value, fail_value, fty_value
            else:
                tested_value = 0
                pass_value = 0
                fail_value = 0
                fty_value = 0
                dpt_value = 0

    return tested_value, pass_value, fail_value, fty_value, dpt_value


@callback(Output(component_id='summary_table', component_property='children'),
          [Input(component_id='Products', component_property='value'),
           Input(component_id='Part_no', component_property='value'),
           Input(component_id='Month', component_property='value'),
           # Input(component_id='interval_db', component_property='n_intervals')
           ])
def summary_table(product, part_no, month):
    filtered = sql_data("raw")
    if product is None:
        if month is None or len(month) == 0:
            if part_no == 'all_values':
                a = table_summary(filtered)
            else:
                b = filtered.loc[filtered['PART_CODE'] == part_no]
                a = table_summary(b)
        else:
            if part_no == 'all_values':
                b = filtered.loc[filtered['MONTH'].isin(month)]
                a = table_summary(b)
            else:
                b = filtered.loc[filtered['MONTH'].isin(month)]
                c = b.loc[b['PART_CODE'] == part_no]
                a = table_summary(c)
    else:
        specific_df = filtered.loc[filtered['PRODUCT_NAME'] == product]
        if month is None or len(month) == 0:
            if part_no == 'all_values':
                a = table_summary(specific_df)
            else:
                b = specific_df.loc[specific_df['PART_CODE'] == part_no]
                a = table_summary(b)
        else:
            if part_no == 'all_values':
                b = specific_df.loc[specific_df['MONTH'].isin(month)]
                a = table_summary(b)
            else:
                b = specific_df.loc[specific_df['MONTH'].isin(month)]
                c = b.loc[b['PART_CODE'] == part_no]
                a = table_summary(c)

    return html.Div([dash_table.DataTable(data=a.to_dict('records'),
                                          columns=[{'name': j, 'id': j} for j in a.columns],
                                          editable=True,
                                          # filter_action="native",
                                          sort_action="native",
                                          sort_mode='multi',
                                          fixed_rows={'headers': True},
                                          style_header={'backgroundColor': "rgb(50, 50, 50)",
                                                        'color': 'white',
                                                        'fontWeight': 'bold',
                                                        'textAlign': 'center', },
                                          style_cell_conditional=[{'if': {'column_index': 0},
                                                                   'fontWeight': 'bold'}],
                                          # Style first row like headers
                                          # style_header={'backgroundColor': "#FFD700",
                                          #               'fontWeight': 'bold',
                                          #               'textAlign': 'center', },
                                          # style_table={'height': 500, 'width': 600, 'overflowX': 'scroll'},
                                          style_cell={'textAlign': 'center', 'height': 'auto',
                                                      'backgroundColor': 'white', 'color': 'black',
                                                      'minWidth': '90px', 'width': '100px',
                                                      'maxWidth': '100px', 'whiteSpace': 'normal',
                                                      },
                                          fill_width=False
                                          ),
                     html.Hr()
                     ])


@callback(Output(component_id='Pie_chart', component_property='figure'),
          [Input(component_id='Products', component_property='value'),
           Input(component_id='Part_no', component_property='value'),
           Input(component_id='Month', component_property='value'),
           # Input(component_id='interval_db', component_property='n_intervals')
           ])
def pie_chart(product, part_no, month):
    filtered_df = sql_data("raw")
    if product is None:
        if month is None or len(month) == 0:
            if part_no == 'all_values':
                pie_df = filtered_df
                a = str(pie_df["FAULT_OBSERVED"].count())
                b = 'Faults Data'
                fig = px.pie(pie_df, names='PRODUCT_NAME', labels='PRODUCT_NAME', hole=0.3)
                # fig.update_layout(margin=dict(b=10))
                fig.update_traces(hovertemplate="Product:%{label} <br>Fault_Count:%{value} <br>Percentage: %{percent}",
                                  textposition='inside'
                                  # textinfo='none'
                                  )
                fig.update_layout(title=b, title_font_size=20, title_pad_b=0, title_y=0.96)
                # fig.update_traces(textinfo='percent+value', insidetextfont_color='black')
                fig.add_annotation(x=0.5, y=0.5, text=a, font=dict(size=12, family='Verdana', color='black'),
                                   showarrow=False)

                # fig.update_layout(legend=dict(orientation='v', yanchor='middle',  y=0.5, xanchor='left',  x=-0.5))
                # yanchor = ['auto', 'top', 'middle', 'bottom'

                fig.update_layout(margin=dict(b=12), plot_bgcolor=colors['background'],
                                  paper_bgcolor=colors['background'], clickmode='event+select',
                                  font_color=colors['text'], uniformtext_minsize=12, uniformtext_mode='hide')
                return fig
            else:
                pie_df = filtered_df.loc[filtered_df['PART_CODE'] == part_no]
                a = str(pie_df["FAULT_OBSERVED"].count())
                b = 'Faults Data for '+part_no
                fig = px.pie(pie_df, names='PRODUCT_NAME', labels='PRODUCT_NAME', hole=0.3)
                # fig.update_layout(margin=dict(b=10))
                fig.update_traces(hovertemplate="Product:%{label} <br>Fault_Count:%{value} <br>Percentage: %{percent}",
                                  textposition='inside')
                # fig.update_traces(textinfo='percent+value', insidetextfont_color='black')
                fig.add_annotation(x=0.5, y=0.5, text=a, font=dict(size=14, family='Verdana', color='black'),
                                   showarrow=False)
                fig.update_layout(title=b, title_font_size=20, title_pad_b=0, title_y=0.96)
                fig.update_layout(margin=dict(b=10), plot_bgcolor=colors['background'],
                                  paper_bgcolor=colors['background'], clickmode='event+select',
                                  font_color=colors['text'], uniformtext_minsize=12, uniformtext_mode='hide')
                return fig
        else:
            if part_no == 'all_values':
                pie_df = filtered_df.loc[filtered_df['MONTH'].isin(month)]
                a = str(pie_df["FAULT_OBSERVED"].count())
                month_name = ",".join(month)
                b = 'Faults Data for ' + month_name
                fig = px.pie(pie_df, names='PRODUCT_NAME', labels='PRODUCT_NAME', hole=0.3)
                # fig.update_layout(margin=dict(b=10))
                fig.update_traces(hovertemplate="Product:%{label} <br>Fault_Count:%{value} <br>Percentage: %{percent}",
                                  textposition='inside')
                # fig.update_traces(textinfo='percent+value', insidetextfont_color='black')
                fig.add_annotation(x=0.5, y=0.5, text=a, font=dict(size=14, family='Verdana', color='black'),
                                   showarrow=False)
                fig.update_layout(title=b, title_font_size=20, title_pad_b=0, title_y=0.96)
                fig.update_layout(margin=dict(b=10), plot_bgcolor=colors['background'],
                                  paper_bgcolor=colors['background'], clickmode='event+select',
                                  font_color=colors['text'], uniformtext_minsize=12, uniformtext_mode='hide')
                return fig
            else:
                df_month_summary = filtered_df.loc[filtered_df['MONTH'].isin(month)]
                pie_df = df_month_summary.loc[df_month_summary['PART_CODE'] == part_no]
                a = str(pie_df["FAULT_OBSERVED"].count())
                b = 'Faults Data for '+part_no
                fig = px.pie(pie_df, names='PRODUCT_NAME', labels='PRODUCT_NAME', hole=0.3)
                # fig.update_layout(margin=dict(b=10))
                fig.update_traces(hovertemplate="Product:%{label} <br>Fault_Count:%{value} <br>Percentage: %{percent}",
                                  textposition='inside')
                # fig.update_traces(textinfo='percent+value', insidetextfont_color='black')
                fig.add_annotation(x=0.5, y=0.5, text=a, font=dict(size=14, family='Verdana', color='black'),
                                   showarrow=False)
                fig.update_layout(title=b, title_font_size=20, title_pad_b=0, title_y=0.96)
                fig.update_layout(margin=dict(b=10), plot_bgcolor=colors['background'],
                                  paper_bgcolor=colors['background'], clickmode='event+select',
                                  font_color=colors['text'], uniformtext_minsize=12, uniformtext_mode='hide')
                return fig

    else:
        specific_df = filtered_df.loc[filtered_df['PRODUCT_NAME'] == product]
        if month is None or len(month) == 0:
            if part_no == 'all_values':
                pie_df = specific_df
                a = str(pie_df["FAULT_OBSERVED"].count())
                b = 'Total Failure for ' + product
            else:
                pie_df = specific_df.loc[specific_df['PART_CODE'] == part_no]
                a = str(pie_df["FAULT_OBSERVED"].count())
                b = 'Faults Data for '+part_no

        else:
            if part_no == 'all_values':
                pie_df = specific_df.loc[specific_df['MONTH'].isin(month)]
                # return the outcomes piechart for a selected month
                a = str(pie_df["FAULT_OBSERVED"].count())
                month_name = ",".join(month)
                b = product + ' Failure for ' + month_name
            else:
                df_month = specific_df.loc[specific_df['MONTH'].isin(month)]
                pie_df = df_month.loc[df_month['PART_CODE'] == part_no]
                a = str(pie_df["FAULT_OBSERVED"].count())
                b = 'Faults Data for '+part_no

    fig = px.pie(pie_df, names='FAULT_OBSERVED', labels='FAULT_OBSERVED', hole=0.3)
    # fig.update_layout(margin=dict(b=10))
    # fig.update_traces(textinfo='percent+value', textfont_size=12, insidetextfont_color='black',
    #                   hovertemplate="Fault:%{label} <br>Count:%{value} <br>Percentage: %{percent}")
    fig.update_traces(hovertemplate="Fault:%{label} <br>Count:%{value} <br>Percentage: %{percent}",
                      textposition='inside')
    fig.add_annotation(x=0.5, y=0.5, text=a, font=dict(size=14, family='Verdana', color='black'),
                       showarrow=False)
    fig.update_layout(title=b, title_font_size=20, title_pad_b=0, title_y=0.96)
    # fig.update_layout(legend=dict(orientation='v', yanchor='middle', y=0.5, xanchor='left', x=-0.5))
    fig.update_layout(margin=dict(b=10), plot_bgcolor=colors['background'], paper_bgcolor=colors['background'],
                      font_color=colors['text'], uniformtext_minsize=12, uniformtext_mode='hide',
                      clickmode='event+select')
    return fig


@callback(Output(component_id='pie_chart1', component_property='figure'),
          [Input(component_id='Product_f2', component_property='value'),
           Input(component_id='Part_no_f2', component_property='value'),
           Input(component_id='Month_f2', component_property='value'),
           # Input(component_id='interval_db', component_property='n_intervals')
           ])
def pie_chart1(product, part_no, month):
    filtered_df = sql_data("raw_f2")
    if product is None:
        if month is None or len(month) == 0:
            if part_no == 'all_values':
                pie_df = filtered_df
                a = str(pie_df["FAULT_OBSERVED"].count())
                b = 'Modules Faults Data'
                fig = px.pie(pie_df, names='PRODUCT_NAME', title=b, hole=0.3)
                fig.update_layout(title_font_size=20, title_pad_b=0, title_y=0.96)
                fig.update_traces(hovertemplate="Product:%{label} <br>Fault_Count:%{value} <br>Percentage: %{percent}",
                                  insidetextfont_color='white', textposition='inside')
                # fig.update_traces(textinfo='percent+value', insidetextfont_color='black')
                fig.add_annotation(x=0.5, y=0.5, text=a, font=dict(size=14, family='Verdana', color='white'),
                                   showarrow=False)
                fig.update_layout(margin=dict(b=10), plot_bgcolor='#1f2c56', paper_bgcolor='#1f2c56',
                                  font_color='white', showlegend=False, uniformtext_minsize=12, uniformtext_mode='hide')
                return fig
            else:
                pie_df = filtered_df.loc[filtered_df['PART_CODE'] == part_no]
                a = str(pie_df["FAULT_OBSERVED"].count())
                b = 'Module Faults Data for '+part_no
                fig = px.pie(pie_df, names='PRODUCT_NAME', title=b, hole=0.3)
                fig.update_layout(title_font_size=20, title_pad_b=0, title_y=0.96)
                fig.update_traces(hovertemplate="Product:%{label} <br>Fault_Count:%{value} <br>Percentage: %{percent}",
                                  insidetextfont_color='white', textposition='inside')
                # fig.update_traces(textinfo='percent+value', insidetextfont_color='black')
                fig.add_annotation(x=0.5, y=0.5, text=a, font=dict(size=14, family='Verdana', color='white'),
                                   showarrow=False)
                fig.update_layout(margin=dict(b=10), plot_bgcolor='#1f2c56', paper_bgcolor='#1f2c56',
                                  font_color='white', showlegend=False, uniformtext_minsize=12, uniformtext_mode='hide')
                return fig
        else:
            if part_no == 'all_values':
                pie_df = filtered_df.loc[filtered_df['MONTH'].isin(month)]
                a = str(pie_df["FAULT_OBSERVED"].count())
                month_name = ",".join(month)
                b = 'Modules Faults Data for ' + month_name
                fig = px.pie(pie_df, names='PRODUCT_NAME', title=b, hole=0.3)
                fig.update_layout(title_font_size=20, title_pad_b=0, title_y=0.96)
                fig.update_traces(hovertemplate="Product:%{label} <br>Fault_Count:%{value} <br>Percentage: %{percent}",
                                  insidetextfont_color='white', textposition='inside')
                # fig.update_traces(textinfo='percent+value', insidetextfont_color='black')
                fig.add_annotation(x=0.5, y=0.5, text=a, font=dict(size=14, family='Verdana', color='white'),
                                   showarrow=False)
                fig.update_layout(margin=dict(b=10), plot_bgcolor='#1f2c56', paper_bgcolor='#1f2c56',
                                  font_color='white', showlegend=False, uniformtext_minsize=12, uniformtext_mode='hide')
                return fig
            else:
                df_month = filtered_df.loc[filtered_df['MONTH'].isin(month)]
                pie_df = df_month.loc[df_month['PART_CODE'] == part_no]
                a = str(pie_df["FAULT_OBSERVED"].count())
                b = 'Module Faults Data for '+part_no
                fig = px.pie(pie_df, names='PRODUCT_NAME', title=b, hole=0.3)
                fig.update_layout(title_font_size=20, title_pad_b=0, title_y=0.96)
                fig.update_traces(hovertemplate="Product:%{label} <br>Fault_Count:%{value} <br>Percentage: %{percent}",
                                  insidetextfont_color='white', textposition='inside')
                # fig.update_traces(textinfo='percent+value', insidetextfont_color='black')
                fig.add_annotation(x=0.5, y=0.5, text=a, font=dict(size=14, family='Verdana', color='white'),
                                   showarrow=False)
                fig.update_layout(margin=dict(b=10), plot_bgcolor='#1f2c56', paper_bgcolor='#1f2c56',
                                  font_color='white', showlegend=False, uniformtext_minsize=12, uniformtext_mode='hide')
                return fig

    else:
        specific_df = filtered_df.loc[filtered_df['PRODUCT_NAME'] == product]
        if month is None or len(month) == 0:
            if part_no == 'all_values':
                pie_df = specific_df
                a = str(pie_df["FAULT_OBSERVED"].count())
                b = 'Total Failure for ' + product
            else:
                pie_df = specific_df.loc[specific_df['PART_CODE'] == part_no]
                a = str(pie_df["FAULT_OBSERVED"].count())
                b = 'Module Faults Data for '+part_no

        else:
            if part_no == 'all_values':
                pie_df = specific_df.loc[specific_df['MONTH'].isin(month)]
                # return the outcomes piechart for a selected month
                a = str(pie_df["FAULT_OBSERVED"].count())
                month_name = ",".join(month)
                b = product + ' Failure for ' + month_name
            else:
                df_month = specific_df.loc[specific_df['MONTH'].isin(month)]
                pie_df = df_month.loc[df_month['PART_CODE'] == part_no]
                a = str(pie_df["FAULT_OBSERVED"].count())
                b = 'Module Faults Data for '+part_no

    fig = px.pie(pie_df, names='FAULT_OBSERVED', title=b, hole=0.3)
    fig.update_layout(title_font_size=20, title_pad_b=0, title_y=0.96)
    fig.update_traces(hovertemplate="Fault:%{label} <br>Count:%{value} <br>Percentage: %{percent}",
                      insidetextfont_color='white', textposition='inside')
    fig.add_annotation(x=0.5, y=0.5, text=a, font=dict(size=14, family='Verdana', color='white'),
                       showarrow=False)
    fig.update_layout(margin=dict(b=10), plot_bgcolor='#1f2c56', paper_bgcolor='#1f2c56',
                      font_color='white', showlegend=False, uniformtext_minsize=12, uniformtext_mode='hide')
    return fig


@callback(Output(component_id='Sunburst', component_property='figure'),
          [Input(component_id='Products', component_property='value'),
           Input(component_id='Part_no', component_property='value'),
           Input(component_id='Month', component_property='value'),
           # Input(component_id='interval_db', component_property='n_intervals')
           ])
def sunburst_chart(product, part_no, month):
    filtered_df = sql_data("raw")
    # map_1 = {'(?)': 'rgb(128, 177, 211)', 'ATS': '#00CC96', 'Initial': 'rgb(36, 121, 108)', 'Burn In': 'red',
    #          'Testing': '#A000ff', 'Pre Initial': '#00ff4f', 'Rack testing': '#Ffe200', 'ATE': '#00CC96',
    #          'TESTING': '#A000ff'}
    colors_df = {'ATE': 'red', 'Pre-initial': '#636EFA', 'Initial': 'orange', 'Burn-in': '#2CA027', 'RT': '#FF6EB4',
                 "TESTING": "#A000ff", "Testing": "#A000ff"}
    if product is None:
        if month is None or len(month) == 0:
            if part_no == 'all_values':
                d = filtered_df
            else:
                d = filtered_df.loc[filtered_df['PART_CODE'] == part_no]
        else:
            if part_no == 'all_values':
                d = filtered_df.loc[filtered_df['MONTH'].isin(month)]
            else:
                a = filtered_df.loc[filtered_df['MONTH'].isin(month)]
                d = a.loc[a['PART_CODE'] == part_no]
    else:
        specific_df = filtered_df.loc[filtered_df['PRODUCT_NAME'] == product]
        if month is None or len(month) == 0:
            if part_no == 'all_values':
                d = specific_df
            else:
                d = specific_df.loc[specific_df['PART_CODE'] == part_no]
        else:
            if part_no == 'all_values':
                d = specific_df.loc[specific_df['MONTH'].isin(month)]
            else:
                a = specific_df.loc[specific_df['MONTH'].isin(month)]
                d = a.loc[a['PART_CODE'] == part_no]

    fig = px.sunburst(d, path=['TOTAL', 'STAGE', 'FAULT_OBSERVED', 'FAULT_CATEGORY', 'KEY_COMPONENT'],
                      maxdepth=2, color='STAGE', custom_data=['STAGE'],
                      color_discrete_map=colors_df)
    fig.update_traces(textinfo='label+value', textfont_size=14, insidetextfont_color='white')
    fig.update_layout(margin=dict(b=10), plot_bgcolor=colors['background'], paper_bgcolor=colors['background'],
                      font_color=colors['text'])
    fig.update_layout(title='Stage wise Fault', title_font_size=20, title_pad_b=0, title_y=0.96)
    fig.update_traces(hovertemplate="Stage:%{customdata} <br>label:%{label} <br>Count:%{value}<br>Parent:%{parent}")
    return fig


@callback(Output(component_id='Bar', component_property='figure'),
          [Input(component_id='Products', component_property='value'),
           Input(component_id='Part_no', component_property='value'),
           Input(component_id='Month', component_property='value'),
           # Input(component_id='interval_db', component_property='n_intervals')
           ])
def bar_chart(product, part_no, month):
    filtered_df = sql_data("raw")
    # map_1 = {'(?)': 'rgb(128, 177, 211)', 'ATS': '#00CC96', 'Initial': 'rgb(36, 121, 108)', 'Burn In': 'red',
    #          'Testing': '#A000ff', 'Pre Initial': '#00ff4f', 'Rack testing': '#Ffe200', 'ATE': '#00CC96',
    #          'TESTING': '#A000ff'}
    if product is None:
        if month is None or len(month) == 0:
            if part_no == 'all_values':
                d = filtered_df
            else:
                d = filtered_df.loc[filtered_df['PART_CODE'] == part_no]
        else:
            if part_no == 'all_values':
                d = filtered_df.loc[filtered_df['MONTH'].isin(month)]
            else:
                a = filtered_df.loc[filtered_df['MONTH'].isin(month)]
                d = a.loc[a['PART_CODE'] == part_no]
    else:
        specific_df = filtered_df.loc[filtered_df['PRODUCT_NAME'] == product]
        if month is None or len(month) == 0:
            if part_no == 'all_values':
                d = specific_df
            else:
                d = specific_df.loc[specific_df['PART_CODE'] == part_no]
        else:
            if part_no == 'all_values':
                d = specific_df.loc[specific_df['MONTH'].isin(month)]
            else:
                a = specific_df.loc[specific_df['MONTH'].isin(month)]
                d = a.loc[a['PART_CODE'] == part_no]

    # bar = d.groupby(['FAULT_OBSERVED', 'STAGE'])['TOTAL'].size().reset_index()
    # bar_1 = d.groupby(['FAULT_OBSERVED', 'STAGE'])['TOTAL'].size().reset_index()
    # df_sorted = bar_1.sort_values('TOTAL', ascending=False)
    # bar = df_sorted.head(20)
    # bar_1 = d.groupby(['FAULT_OBSERVED', 'STAGE'])['TOTAL'].size().reset_index()
    # bar_1['Percentage'] = bar_1['TOTAL'] / bar_1['TOTAL'].sum() * 100
    # bar_top20 = d.groupby('FAULT_OBSERVED')['TOTAL'].size().nlargest(20).reset_index()
    # bar_2 = bar_1[bar_1['FAULT_OBSERVED'].isin(bar_top20['FAULT_OBSERVED'])]
    # bar = bar_2.sort_values('TOTAL', ascending=False)
    #
    # fig = px.bar(bar, x='TOTAL', y='FAULT_OBSERVED', title="Faults Type", color='STAGE', text='TOTAL',
    #              color_discrete_map=map_1, custom_data=['STAGE', 'FAULT_OBSERVED', 'Percentage'])
    # shortened_labels = [label[:25] + '...' if len(label) > 25 else label for label in bar['FAULT_OBSERVED']]
    # hovertemplate = '<b>%{customdata[1]}<br>Fault_Count: %{x}<br>Fault_Percent: %{customdata[2]:.2f}%' \
    #                 '<br>STAGE: %{customdata[0]}'
    # fig.update_traces(hovertemplate=hovertemplate)
    # fig.update_layout(yaxis={'ticktext': shortened_labels, 'tickvals': bar['FAULT_OBSERVED']})
    # fig.update_traces(textfont_size=20, textangle=0, textposition="inside", cliponaxis=False,
    #                   insidetextfont_color='black')
    # fig.update_layout(margin=dict(b=10), plot_bgcolor=colors['background'], paper_bgcolor=colors['background'],
    #                   font_color=colors['text'])
    # fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    # return fig

    bar = pd.crosstab(d["FAULT_OBSERVED"], d["STAGE"])
    bar = bar.reset_index()
    bar['Total'] = bar.sum(axis=1, numeric_only=True)
    # Sort the DataFrame based on the 'Total' column in descending order
    bar = bar.sort_values('Total', ascending=False)
    # Take only the top 20 rows
    bar = bar.head(20)
    bar = bar.drop(['Total'], axis=1)

    df_1 = pd.DataFrame({'Faults': bar["FAULT_OBSERVED"]})

    for stage in bar.columns[1:]:
        df_1[stage] = bar[stage]
    # colors
    colors_df = {'ATE': 'red', 'Pre-initial': '#636EFA', 'Initial': 'orange', 'Burn-in': '#2CA027', 'RT': '#FF6EB4',
                 "TESTING": "#A000ff", "Testing": "#A000ff"}
    # colors = {'ATE': '#00CC96',
    #           'Pre-initial': '#rgb(128, 177, 211)', 'Initial': 'rgb(36, 121, 108)', 'Burn-in': '#Ffe200',
    #           "RT": "00ff4f", "TESTING": "#A000ff"}

    data = []
    # loop across the different rows
    for i in range(df_1.shape[0]):
        row = df_1.iloc[i]
        fault = row['Faults']
        stages = row.index[1:]
        counts = row[1:]
        ordered_stages = stages[np.argsort(counts)][::-1]
        for stage in ordered_stages:
            count = counts[stage]
            trace_data = pd.DataFrame({'Faults': [fault], 'Count': [count], 'Stage': [stage]})
            trace = px.bar(data_frame=trace_data, y='Faults', x='Count', color='Stage',
                           color_discrete_map=colors_df, labels=None, custom_data=['Stage', 'Count', 'Faults'])
            trace.update_traces(texttemplate='%{customdata[1]}', textfont_size=20, textangle=0, textposition="inside",
                                cliponaxis=False, insidetextfont_color='white')
            data.append(trace)

    fig = data[0]
    for trace in data[1:]:
        fig.add_trace(trace.data[0])

    fig.update_layout(title="Faults Type", title_font_size=20, title_pad_b=0, title_y=0.96)
    shortened_labels = [label[:25] + '...' if len(label) > 25 else label for label in bar['FAULT_OBSERVED']]
    hovertemplate = '%{customdata[2]}<br>Fault_Count: %{customdata[1]}<br>STAGE: %{customdata[0]}'
    fig.update_traces(hovertemplate=hovertemplate)

    fig.update_layout(yaxis={'ticktext': shortened_labels, 'tickvals': bar['FAULT_OBSERVED']})
    fig.update_layout(margin=dict(b=10), plot_bgcolor=colors['background'], paper_bgcolor=colors['background'],
                      font_color=colors['text'])
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})  # for sorting the data in descending order
    # fig.update_layout(showlegend=False)

    unique_legends = set()
    # Iterate over each bar trace
    for trace in fig.data:
        legend_text = trace.name
        # Check if the legend is unique
        if legend_text not in unique_legends:
            unique_legends.add(legend_text)
            trace.showlegend = True
        else:
            trace.showlegend = False

    fig.update_layout(legend=dict(orientation="v",
                                  x=1,
                                  y=1,
                                  title_font_family="Sitka Small",
                                  title='<span style="text-transform: uppercase;">STAGE</span>'))
    return fig


@callback(Output(component_id='Bar1', component_property='figure'),
          [Input(component_id='Product_f2', component_property='value'),
           Input(component_id='Part_no_f2', component_property='value'),
           Input(component_id='Month_f2', component_property='value'),
           # Input(component_id='interval_db', component_property='n_intervals')
           ])
def bar_chart1(product, part_no, month):
    filtered_df = sql_data("raw_f2")
    # map_1 = {'(?)': 'rgb(128, 177, 211)', 'ATS': '#00CC96', 'Initial': 'rgb(36, 121, 108)', 'Burn In': 'red',
    #          'Testing': '#A000ff', 'Pre Initial': '#00ff4f', 'Rack testing': '#Ffe200', 'ATE': '#00CC96',
    #          'TESTING': '#A000ff', 'RT': 'pink'}
    if product is None:
        if month is None or len(month) == 0:
            if part_no == 'all_values':
                d = filtered_df
            else:
                d = filtered_df.loc[filtered_df['PART_CODE'] == part_no]
        else:
            if part_no == 'all_values':
                d = filtered_df.loc[filtered_df['MONTH'].isin(month)]
            else:
                a = filtered_df.loc[filtered_df['MONTH'].isin(month)]
                d = a.loc[a['PART_CODE'] == part_no]
    else:
        specific_df = filtered_df.loc[filtered_df['PRODUCT_NAME'] == product]
        if month is None or len(month) == 0:
            if part_no == 'all_values':
                d = specific_df
            else:
                d = specific_df.loc[specific_df['PART_CODE'] == part_no]
        else:
            if part_no == 'all_values':
                d = specific_df.loc[specific_df['MONTH'].isin(month)]
            else:
                a = specific_df.loc[specific_df['MONTH'].isin(month)]
                d = a.loc[a['PART_CODE'] == part_no]

    # bar_1 = d.groupby(['FAULT_OBSERVED', 'STAGE'])['TOTAL'].size().reset_index()
    # bar_1['Percentage'] = bar_1['TOTAL'] / bar_1['TOTAL'].sum() * 100
    # bar_top20 = d.groupby('FAULT_OBSERVED')['TOTAL'].size().nlargest(20).reset_index()
    # bar_2 = bar_1[bar_1['FAULT_OBSERVED'].isin(bar_top20['FAULT_OBSERVED'])]
    # bar = bar_2.sort_values('TOTAL', ascending=False)

    bar = pd.crosstab(d["FAULT_OBSERVED"], d["STAGE"])
    bar = bar.reset_index()
    bar['Total'] = bar.sum(axis=1, numeric_only=True)
    # Sort the DataFrame based on the 'Total' column in descending order
    bar = bar.sort_values('Total', ascending=False)
    # Take only the top 20 rows
    bar = bar.head(20)
    bar = bar.drop(['Total'], axis=1)

    df_1 = pd.DataFrame({'Faults': bar["FAULT_OBSERVED"]})

    for stage in bar.columns[1:]:
        df_1[stage] = bar[stage]
    # colors
    colors_df = {'ATE': 'red', 'Pre-initial': '#636EFA', 'Initial': 'orange', 'Burn-in': '#2CA027', 'RT': '#FF6EB4',
                 "TESTING": "#A000ff", "Testing": "#A000ff"}

    # colors = {'ATE': '#00CC96',
    #           'Pre-initial': '#rgb(128, 177, 211)', 'Initial': 'rgb(36, 121, 108)', 'Burn-in': '#Ffe200',
    #           "RT": "00ff4f", "TESTING": "#A000ff"}
    # traces
    data = []
    # loop across the different rows
    for i in range(df_1.shape[0]):
        row = df_1.iloc[i]
        fault = row['Faults']
        stages = row.index[1:]
        counts = row[1:]
        ordered_stages = stages[np.argsort(counts)][::-1]
        for stage in ordered_stages:
            count = counts[stage]
            trace_data = pd.DataFrame({'Faults': [fault], 'Count': [count], 'Stage': [stage]})
            trace = px.bar(data_frame=trace_data, y='Faults', x='Count', color='Stage', title="Faults Type",
                           color_discrete_map=colors_df, labels=None, custom_data=['Stage', 'Count', 'Faults'])
            trace.update_traces(texttemplate='%{customdata[1]}', textfont_size=14, textangle=0, textposition="inside",
                                cliponaxis=False, insidetextfont_color='white')
            data.append(trace)

            # custom_data = [stage, fault]  # Customize customdata as per your requirements
            # data.append(px.bar(data_frame=trace_data, y='Faults', x='Count', color='Stage',
            #                    color_discrete_map=colors, labels=None, custom_data=['Stage', 'Count']))

    # layout
    # layout = dict(barmode='stack',
    #               xaxis={'title': "Faults count"},
    #               yaxis={'type': 'category', 'title': 'Faults'})
    fig = data[0]
    for trace in data[1:]:
        fig.add_trace(trace.data[0])

    fig.update_layout(title_font_size=20, title_pad_b=0, title_y=0.96)
    shortened_labels = [label[:25] + '...' if len(label) > 25 else label for label in bar['FAULT_OBSERVED']]
    hovertemplate = '%{customdata[2]}<br>Fault_Count: %{customdata[1]}<br>STAGE: %{customdata[0]}'
    fig.update_traces(hovertemplate=hovertemplate)

    fig.update_layout(yaxis={'ticktext': shortened_labels, 'tickvals': bar['FAULT_OBSERVED']})
    fig.update_layout(margin=dict(b=10), plot_bgcolor='#1f2c56', paper_bgcolor='#1f2c56',
                      font_color='white')
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})  # for sorting the data in descending order
    # fig.update_layout(showlegend=False)

    unique_legends = set()
    # Iterate over each bar trace
    for trace in fig.data:
        legend_text = trace.name
        # Check if the legend is unique
        if legend_text not in unique_legends:
            unique_legends.add(legend_text)
            trace.showlegend = True
        else:
            trace.showlegend = False

    # fig.update_traces(textfont_size=14, textangle=0, textposition="inside", cliponaxis=False,
    #                   insidetextfont_color='white')
    fig.update_layout(legend=dict(orientation="v",
                                  x=1,
                                  y=1,
                                  title_font_family="Sitka Small", title='<span style="text-transform: uppercase;">STAGE</span>'))

    # bar_1['Percentage'] = bar_1['TOTAL'] / bar_1['TOTAL'].sum() * 100

    # fig = px.bar(bar, x='TOTAL', y='FAULT_OBSERVED', title="Faults Type", color='STAGE', text='TOTAL',
    #              color_discrete_map=map_1, custom_data=['STAGE', 'FAULT_OBSERVED', 'Percentage'], barmode='relative')


    # fig.update_layout(title_font_size=20, title_pad_b=0, title_y=0.96)
    # # fig.update_layout(hovermode='x')
    # shortened_labels = [label[:25] + '...' if len(label) > 25 else label for label in bar['FAULT_OBSERVED']]
    # # hovertemplate = '<b>%{y}</b><br>Fault_Count: %{x}<br>STAGE: %{customdata[0]}'
    #
    # # hovertemplate = '<b>%{customdata[1]}<br>Fault_Count: %{x}<br>Fault_Percent: %{customdata[2]:.2f}%' \
    # #                 '<br>STAGE: %{customdata[0]}'
    # # fig.update_traces(hovertemplate=hovertemplate)'
    # fig.update_traces(textfont_size=14, textangle=0, textposition="inside", cliponaxis=False,
    #                   insidetextfont_color='white')
    # fig.update_layout(yaxis={'ticktext': shortened_labels, 'tickvals': bar['FAULT_OBSERVED']})
    # fig.update_layout(margin=dict(b=10), plot_bgcolor='#1f2c56', paper_bgcolor='#1f2c56',
    #                   font_color='white')
    # fig.update_layout(yaxis={'categoryorder': 'total ascending'})  # for sorting the data in descending order
    # # fig.update_layout(barmode='relative')
    return fig


@callback(Output(component_id='Category_bar', component_property='figure'),
          [Input(component_id='Products', component_property='value'),
           Input(component_id='Part_no', component_property='value'),
           Input(component_id='Month', component_property='value'),
           # Input(component_id='interval_db', component_property='n_intervals')
           ])
def category_bar(product, part_no, month):
    filtered_df = sql_data("raw")
    # map_1 = {'(?)': 'rgb(128, 177, 211)', 'ATS': '#00CC96', 'Initial': 'rgb(36, 121, 108)', 'Burn In': 'red',
    #          'Testing': '#A000ff', 'Pre Initial': '#00ff4f', 'Rack testing': '#Ffe200', 'ATE': '#00CC96',
    #          'TESTING': '#A000ff'}
    if product is None:
        if month is None or len(month) == 0:
            if part_no == 'all_values':
                d = filtered_df
            else:
                d = filtered_df.loc[filtered_df['PART_CODE'] == part_no]
        else:
            if part_no == 'all_values':
                d = filtered_df.loc[filtered_df['MONTH'].isin(month)]
            else:
                a = filtered_df.loc[filtered_df['MONTH'].isin(month)]
                d = a.loc[a['PART_CODE'] == part_no]
    else:
        specific_df = filtered_df.loc[filtered_df['PRODUCT_NAME'] == product]
        if month is None or len(month) == 0:
            if part_no == 'all_values':
                d = specific_df
            else:
                d = specific_df.loc[specific_df['PART_CODE'] == part_no]
        else:
            if part_no == 'all_values':
                d = specific_df.loc[specific_df['MONTH'].isin(month)]
            else:
                a = specific_df.loc[specific_df['MONTH'].isin(month)]
                d = a.loc[a['PART_CODE'] == part_no]

    bar = pd.crosstab(d["FAULT_CATEGORY"], d["STAGE"])
    bar = bar.reset_index()
    bar['Total'] = bar.sum(axis=1, numeric_only=True)
    # Sort the DataFrame based on the 'Total' column in descending order
    bar = bar.sort_values('Total', ascending=False)
    # Take only the top 20 rows
    bar = bar.head(10)
    bar = bar.drop(['Total'], axis=1)

    df_1 = pd.DataFrame({'Faults': bar["FAULT_CATEGORY"]})

    for stage in bar.columns[1:]:
        df_1[stage] = bar[stage]
    # colors

    colors_df = {'ATE': 'red', 'Pre-initial': '#636EFA', 'Initial': 'orange', 'Burn-in': '#2CA027', 'RT': '#FF6EB4',
                 "TESTING": "#A000ff", "Testing": "#A000ff"}

    # colors = {'ATE': '#00CC96',
    #           'Pre-initial': '#rgb(128, 177, 211)', 'Initial': 'rgb(36, 121, 108)', 'Burn-in': '#Ffe200',
    #           "RT": "00ff4f", "TESTING": "#A000ff"}

    data = []
    # loop across the different rows
    for i in range(df_1.shape[0]):
        row = df_1.iloc[i]
        fault = row['Faults']
        stages = row.index[1:]
        counts = row[1:]
        ordered_stages = stages[np.argsort(counts)][::-1]
        for stage in ordered_stages:
            count = counts[stage]
            trace_data = pd.DataFrame({'Faults': [fault], 'Count': [count], 'Stage': [stage]})
            trace = px.bar(data_frame=trace_data, y='Faults', x='Count', color='Stage',
                           color_discrete_map=colors_df, labels=None, custom_data=['Stage', 'Count', 'Faults'])
            # trace = px.bar(data_frame=trace_data, y='Faults', x='Count', color='Stage',
            #                labels=None, custom_data=['Stage', 'Count', 'Faults'])
            trace.update_traces(texttemplate='%{customdata[1]}', textfont_size=20, textangle=0, textposition="inside",
                                cliponaxis=False, insidetextfont_color='white')
            data.append(trace)

    fig = data[0]
    for trace in data[1:]:
        fig.add_trace(trace.data[0])

    fig.update_layout(title="Faults Category", title_font_size=20, title_pad_b=0, title_y=0.96)
    shortened_labels = [label[:25] + '...' if len(label) > 25 else label for label in bar['FAULT_CATEGORY']]
    hovertemplate = '%{customdata[2]}<br>Fault_Count: %{customdata[1]}<br>STAGE: %{customdata[0]}'
    fig.update_traces(hovertemplate=hovertemplate)

    fig.update_layout(yaxis={'ticktext': shortened_labels, 'tickvals': bar['FAULT_CATEGORY']})
    fig.update_layout(margin=dict(b=10), plot_bgcolor=colors['background'], paper_bgcolor=colors['background'],
                      font_color=colors['text'])
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})  # for sorting the data in descending order
    # fig.update_layout(showlegend=False)

    unique_legends = set()
    # Iterate over each bar trace
    for trace in fig.data:
        legend_text = trace.name
        # Check if the legend is unique
        if legend_text not in unique_legends:
            unique_legends.add(legend_text)
            trace.showlegend = True
        else:
            trace.showlegend = False

    fig.update_layout(legend=dict(orientation="v",
                                  x=1,
                                  y=1,
                                  title_font_family="Sitka Small",
                                  title='<span style="text-transform: uppercase;">STAGE</span>'))
    return fig


@callback(Output(component_id='List of Faults', component_property='options'),
          [Input(component_id='Products_table', component_property='value'),
           Input(component_id='Month_table', component_property='value'),
           # Input(component_id='interval_db', component_property='n_intervals')
           ])
# Input(component_id='List of Faults', component_property='search_value'), with this we have to add a another value in
# dropdown_faults function
def dropdown_faults(product, month):
    filtered_df = sql_data("raw")
    if product is None:
        if month is None or len(month) == 0:
            d = filtered_df
        else:
            d = filtered_df.loc[filtered_df['MONTH'].isin(month)]
            # return [{"label": i, "value": i} for i in fault[month]]
    else:
        specific_df = filtered_df.loc[filtered_df['PRODUCT_NAME'] == product]
        if month is None or len(month) == 0:
            d = specific_df
        else:
            d = specific_df.loc[specific_df['MONTH'].isin(month)]

    return [{"label": j, "value": j} for j in d['FAULT_OBSERVED'].unique()]


@callback(Output(component_id='Faults_list', component_property='children'),
          [Input(component_id='List of Faults', component_property='value'),
           Input(component_id='Products_table', component_property='value'),
           Input(component_id='Month_table', component_property='value'),
           # Input(component_id='interval_db', component_property='n_intervals')
           ])
def display_table(dropdown_value, product, month):
    filtered = df
    if product is None:
        if dropdown_value is None:
            if month is None or len(month) == 0:
                a = filtered
            else:
                a = filtered.loc[filtered['MONTH'].isin(month)]
        else:
            specific = filtered.loc[filtered['FAULT_OBSERVED'] == dropdown_value]
            if month is None:
                a = specific
            else:
                a = specific.loc[specific['MONTH'].isin(month)]
    else:
        specific_df = filtered.loc[filtered['PRODUCT_NAME'] == product]
        if dropdown_value is None:
            if month is None or len(month) == 0:
                a = specific_df
            else:
                a = specific_df.loc[specific_df['MONTH'].isin(month)]
        else:
            specific = specific_df.loc[specific_df['FAULT_OBSERVED'] == dropdown_value]
            if month is None:
                a = specific
            else:
                a = specific.loc[specific['MONTH'].isin(month)]

    return html.Div([dash_table.DataTable(data=a.to_dict('records'),
                                          columns=[{'name': j, 'id': j} for j in a.columns],
                                          editable=True,
                                          filter_action="native",
                                          sort_action="native",
                                          sort_mode='multi',
                                          fixed_rows={'headers': True},
                                          style_header={'backgroundColor': "rgb(50, 50, 50)",
                                                        'color': 'white',
                                                        'fontWeight': 'bold',
                                                        'textAlign': 'center', },
                                          # style_header={'backgroundColor': "#FFD700",
                                          #               'fontWeight': 'bold',
                                          #               'textAlign': 'center', },
                                          style_table={'height': 420, 'overflowX': 'scroll'},
                                          style_cell={'minWidth': '130px', 'width': '140px',
                                                      'maxWidth': '130px', 'whiteSpace': 'normal',
                                                      'textAlign': 'center',
                                                      'backgroundColor': 'white', 'color': 'black'}, ),
                     html.Hr()
                     ])


@callback(Output(component_id='Product_f2', component_property='options'),
          [Input(component_id='Month_f2', component_property='value'),
           Input(component_id='Part_no_f2', component_property='value')
          # Input(component_id='interval_db', component_property='n_intervals')
           ])
def dropdown_faults_f2(month, part_no):
    df_raw2 = sql_data("card_f2")
    # filtered_df = df_raw2.loc[df_raw2['PRODUCT'].isin(modules)]
    filtered_df = df_raw2
    if month is None or len(month) == 0:
        if part_no == "all_values":
            d = filtered_df
        else:
            d = filtered_df.loc[filtered_df['PART_CODE'] == part_no]
    else:
        specific = filtered_df.loc[filtered_df['MONTH'].isin(month)]
        if part_no == "all_values":
            d = specific
        else:
            d = specific.loc[specific['PART_CODE'] == part_no]

    return [{"label": j, "value": j}for j in d['PRODUCT'].unique()]


@callback(Output(component_id='stages', component_property='options'),
          Input(component_id='Product_f2', component_property='value'),
          # Input(component_id='interval_db', component_property='n_intervals')
          )
def dropdown_stages(product):
    df_raw2_f2 = sql_data("raw")
    modules_f2 = ['2KW SMR', '3KW SMR', '4KW SMR', 'SMR_2KW_SOLAR', 'SMR_3KW_SOLAR', 'CHARGER', 'M1000', 'M2000',
                  'WCBMS', '2KW SUN MOBILITY', 'SMR_1.1KW', 'CHARGER_1.1KW', 'DCIO_F2']
    df_raw2 = df_raw2_f2.loc[df_raw2_f2['PRODUCT_NAME'].isin(modules_f2)]
    filtered_df = df_raw2.sort_values(by=['STAGE'], ascending=False)
    if product is None:
        d = filtered_df
    else:
        d = filtered_df.loc[filtered_df['PRODUCT_NAME'] == product]

    return [{"label": j, "value": j} for j in d['STAGE'].unique()]


@callback(
    Output('stages', 'value'),
    [Input('stages', 'options'),
     Input('Product_f2', 'value'),
     # Input('interval_db', 'n_intervals')
     ])
def set_stages_value(available_options, product):
    if product is None:
        return None
    else:
        return available_options[0]['value']


@callback(Output(component_id='Part_no', component_property='options'),
          [Input(component_id='Products', component_property='value'),
           Input(component_id='Month', component_property='value'),
           # Input(component_id='interval_db', component_property='n_intervals')
           ])
def dropdown_part_no_summary(product, month):
    filtered_df = sql_data("card_part")
    if product is None:
        if month is None or len(month) == 0:
            d = filtered_df
        else:
            d = filtered_df.loc[filtered_df['MONTH'].isin(month)]
    else:
        specific = filtered_df.loc[filtered_df['PRODUCT'] == product]
        if month is None or len(month) == 0:
            d = specific
        else:
            d = specific.loc[specific['MONTH'].isin(month)]
    return [{"label": j, "value": j} for j in d['PART_CODE'].unique()]+[{'label': 'Select all', 'value': 'all_values'}]


@callback(
    Output('Part_no', 'value'),
    [Input('Part_no', 'options'),
     Input('Products', 'value'),
     # Input('interval_db', 'n_intervals')
     ])
def set_part_no_value(available_options, product):
    if product is None:
        return available_options[-1]['value']
    else:
        return available_options[-1]['value']

# @callback(
#     Output('Products', 'value'),
#     [Input('Products', 'options'),
#      Input('Part_no', 'value'),
#      # Input('interval_db', 'n_intervals')
#      ])
# def set_product_summary_value(available_options, part_no):
#     if part_no != 'all_values':
#         return available_options[-1]['value']


@callback(Output(component_id='Month', component_property='options'),
          [Input(component_id='Products', component_property='value'),
           Input(component_id='Part_no', component_property='value'),
           # Input(component_id='interval_db', component_property='n_intervals')
           ])
def dropdown_month(product, part_no):
    df_all = sql_data("card")
    filtered_df = df_all
    if product is None:
        if part_no == "all_values":
            d = filtered_df
        else:
            d = filtered_df.loc[filtered_df['PART_CODE'] == part_no]
    else:
        specific = filtered_df.loc[filtered_df['PRODUCT'] == product]
        if part_no == "all_values":
            d = specific
        else:
            d = specific.loc[specific['PART_CODE'] == part_no]

    final_month_list = month_data(d)

    return [{"label": j, "value": j}for j in final_month_list]


# @callback(
#     Output(component_id='Month', component_property='value'),
#     [Input(component_id='Month', component_property='options')]
# )
# def set_default_month(options):
#     df_all = sql_data("card")
#     filtered_df = df_all
#     final_month_list = month_data(filtered_df)
#     latest_month = final_month_list[-1]
#     # latest_month = max(options, key=lambda x: datetime.datetime.strptime(x['value'], "%b,%d"))['value']
#     return [latest_month]


# @callback(
#     Output('Month', 'value'),
#     [Input('Month', 'options'),
#      Input('Products', 'value'),
#      # Input('interval_db', 'n_intervals')
#      ])
# def set_month_value(available_options, product):
#     if product is None:
#         return available_options[-1]['value']
#     else:
#         return available_options[-1]['value']


@callback(Output(component_id='Month_f2', component_property='options'),
          [Input(component_id='Product_f2', component_property='value'),
           Input(component_id='Part_no_f2', component_property='value')
           ])
def dropdown_month_f2(product, part_no):
    # modules = ['2KW SMR', '3KW SMR', '4KW SMR', 'SMR_2KW_SOLAR', 'SMR_3KW_SOLAR', 'CHARGER', 'M1000', 'M2000',
    # 'WCBMS', 'SMR_1.1KW', 'CHARGER_1.1KW']
    df_card_summary = sql_data("card_f2")
    # filtered_df = df_raw2.loc[df_raw2['PRODUCT_NAME'].isin(modules)]
    filtered_df = df_card_summary
    if product is None:
        if part_no == "all_values":
            d = filtered_df
        else:
            d = filtered_df.loc[filtered_df['PART_CODE'] == part_no]
    else:
        specific = filtered_df.loc[filtered_df['PRODUCT'] == product]
        if part_no == "all_values":
            d = specific
        else:
            d = specific.loc[specific['PART_CODE'] == part_no]

    final_month_list = month_data(d)

    return [{"label": j, "value": j}for j in final_month_list]


@callback(Output(component_id='Part_no_f2', component_property='options'),
          [Input(component_id='Product_f2', component_property='value'),
           Input(component_id='Month_f2', component_property='value'),
           # Input(component_id='interval_db', component_property='n_intervals')
           ])
def dropdown_part_no_f2(product, month):
    filtered_df = sql_data("card_part_f2")

    if product is None:
        if month is None or len(month) == 0:
            d = filtered_df
        else:
            d = filtered_df.loc[filtered_df['MONTH'].isin(month)]
    else:
        specific = filtered_df.loc[filtered_df['PRODUCT'] == product]
        if month is None or len(month) == 0:
            d = specific
        else:
            d = specific.loc[specific['MONTH'].isin(month)]
    return [{"label": j, "value": j} for j in d['PART_CODE'].unique()]+[{'label': 'Select all', 'value': 'all_values'}]


@callback(
    Output('Part_no_f2', 'value'),
    [Input('Part_no_f2', 'options'),
     Input('Product_f2', 'value'),
     # Input('interval_db', 'n_intervals')
     ])
def set_part_no_f2_value(available_options, product):
    if product is None:
        return available_options[-1]['value']
    else:
        return available_options[-1]['value']

# def logo():
#     return html.Img(src=app.get_asset_url('logo.png'))

# @callback(
#     Output('Product_f2', 'value'),
#     [Input('Product_f2', 'options'),
#      Input('Part_no_f2', 'value'),
#      # Input('interval_db', 'n_intervals')
#      ])
# def set_product_f2_value(available_options, part_no):
#     if part_no != 'all_values':
#         return available_options[-1]['value']


@callback([Output('Tested', 'figure'),
           Output('Pass1', 'figure'),
           Output('Fail', 'figure'),
           Output('%Fail', 'figure'),
           Output('DPT', 'figure'), ],
          [Input('stages', 'value'),
           Input('Month_f2', 'value'),
           Input('Part_no_f2', 'value'),
           Input('Product_f2', 'value'),
           # Input('interval_db', 'n_intervals')
           ])
def update_confirmed(stages, month, part_no, product):
    smr = sql_data("smr_total")
    mcm = sql_data("mcm_total")
    # smr_month = df_smr_month
    # mcm_month = df_mcm_month
    smr_part = sql_data("smr_part")
    mcm_part = sql_data("mcm_part")
    if stages is not None and stages != 'RT':
        # a = stages.upper().replace(" ", "_")
        a = stages.upper().replace("-", "_")
        test_stage = a + '_TEST_QUANTITY'
        pass_stage = a + '_PASS_QUANTITY'
        fail_stage = a + '_FAIL_QUANTITY'
        if month is None or len(month) == 0:
            if part_no == 'all_values':
                if (product == 'SMR_2KW_SOLAR') or (product == '3KW SMR') or (product == '2KW SMR') or \
                        (product == 'CHARGER') or (product == 'SMR_3KW_SOLAR') or (product == '4KW SMR'):
                    test_value = smr[test_stage].loc[product]
                    pass_value = smr[pass_stage].loc[product]
                    fail_value = smr[fail_stage].loc[product]
                else:
                    test_value = mcm[test_stage].loc[product]
                    pass_value = mcm[pass_stage].loc[product]
                    fail_value = mcm[fail_stage].loc[product]
            else:
                specific_smr = smr_part.loc[smr_part['PART_CODE'] == part_no]
                specific_mcm = mcm_part.loc[mcm_part['PART_CODE'] == part_no]
                if (product == 'SMR_2KW_SOLAR') or (product == '3KW SMR') or (product == '2KW SMR') or \
                        (product == 'CHARGER') or (product == 'SMR_3KW_SOLAR') or (product == '4KW SMR'):
                    test_value = specific_smr[test_stage].loc[product].sum()
                    pass_value = specific_smr[pass_stage].loc[product].sum()
                    fail_value = specific_smr[fail_stage].loc[product].sum()
                else:
                    test_value = specific_mcm[test_stage].loc[product].sum()
                    pass_value = specific_mcm[pass_stage].loc[product].sum()
                    fail_value = specific_mcm[fail_stage].loc[product].sum()
        else:
            if part_no == 'all_values':
                if (product == 'SMR_2KW_SOLAR') or (product == '3KW SMR') or (product == '2KW SMR') or \
                        (product == 'CHARGER') or (product == 'SMR_3KW_SOLAR') or (product == '4KW SMR'):
                    specific_smr = smr_part.loc[smr_part['MONTH'].isin(month)]
                    test_value = specific_smr[test_stage].loc[product].sum()
                    pass_value = specific_smr[pass_stage].loc[product].sum()
                    fail_value = specific_smr[fail_stage].loc[product].sum()
                else:
                    specific_mcm = mcm_part.loc[mcm_part['MONTH'].isin(month)]
                    test_value = specific_mcm[test_stage].loc[product].sum()
                    pass_value = specific_mcm[pass_stage].loc[product].sum()
                    fail_value = specific_mcm[fail_stage].loc[product].sum()
            else:
                specific_smr = smr_part.loc[smr_part['MONTH'].isin(month)]
                filtered_smr = specific_smr.loc[specific_smr['PART_CODE'] == part_no]
                specific_mcm = mcm_part.loc[mcm_part['MONTH'].isin(month)]
                filtered_mcm = specific_mcm.loc[specific_mcm['PART_CODE'] == part_no]
                if (product == 'SMR_2KW_SOLAR') or (product == '3KW SMR') or (product == '2KW SMR') or \
                        (product == 'CHARGER') or (product == 'SMR_3KW_SOLAR') or (product == '4KW SMR'):
                    test_value = filtered_smr[test_stage].loc[product]
                    pass_value = filtered_smr[pass_stage].loc[product]
                    fail_value = filtered_smr[fail_stage].loc[product]
                else:
                    test_value = filtered_mcm[test_stage].loc[product]
                    pass_value = filtered_mcm[pass_stage].loc[product]
                    fail_value = filtered_mcm[fail_stage].loc[product]
        value_confirmed_test = test_value
        value_confirmed_pass = pass_value
        value_confirmed_fail = fail_value
        value_confirmed_fty = (round((pass_value / test_value) * 100, 1))
        value_confirmed_dpt = (int(round(((fail_value / test_value) * 1000), 0)))
    elif stages == 'RT':
        tested_value, pass_value, fail_value, fty_value, dpt_value = test_count(product, part_no, month)
        value_confirmed_test = int(tested_value)
        value_confirmed_pass = int(pass_value)
        value_confirmed_fail = int(fail_value)
        fty_data = fty_value[:-1]
        value_confirmed_fty = float(fty_data)
        value_confirmed_dpt = int(dpt_value)
    else:
        value_confirmed_test = 0
        value_confirmed_pass = 0
        value_confirmed_fail = 0
        value_confirmed_fty = 0
        value_confirmed_dpt = 0

    return {
        'data': [go.Indicator(
            mode='number',
            value=value_confirmed_test,
            # delta={'reference': delta_confirmed,
            #        'position': 'right',
            #        'valueformat': ',g',
            #        'relative': False,
            #
            #        'font': {'size': 15}},
            number={'font': {'size': 20}, },
            domain={'y': [0, 1], 'x': [0, 1]})],
        'layout': go.Layout(
                title={'text': 'Tested',
                       'y': 1,
                       'x': 0.5,
                       'xanchor': 'center',
                       'yanchor': 'top'},
                font=dict(color='orange'),
                paper_bgcolor='#1f2c56',
                plot_bgcolor='#1f2c56',
                height=50
                ), }, {
        'data': [go.Indicator(
            mode='number',
            value=value_confirmed_pass,
            # delta={'reference': delta_confirmed,
            #        'position': 'right',
            #        'valueformat': ',g',
            #        'relative': False,
            #
            #        'font': {'size': 15}},
            number={'font': {'size': 20}, },
            domain={'y': [0, 1], 'x': [0, 1]})],
        'layout': go.Layout(
                title={'text': 'Pass',
                       'y': 1,
                       'x': 0.5,
                       'xanchor': 'center',
                       'yanchor': 'top'},
                font=dict(color='lime'),
                paper_bgcolor='#1f2c56',
                plot_bgcolor='#1f2c56',
                height=50
                ), }, {
        'data': [go.Indicator(
            mode='number',
            value=value_confirmed_fail,
            # delta={'reference': delta_confirmed,
            #        'position': 'right',
            #        'valueformat': ',g',
            #        'relative': False,
            #
            #        'font': {'size': 15}},
            number={'font': {'size': 20}, },
            domain={'y': [0, 1], 'x': [0, 1]})],
        'layout': go.Layout(
                title={'text': 'Fail',
                       'y': 1,
                       'x': 0.5,
                       'xanchor': 'center',
                       'yanchor': 'top'},
                font=dict(color='red'),
                paper_bgcolor='#1f2c56',
                plot_bgcolor='#1f2c56',
                height=50
                ), }, {
        'data': [go.Indicator(
            mode='number+delta',
            value=value_confirmed_fty,
            # delta={'reference': delta_confirmed,
            #        'position': 'right',
            #        'valueformat': ',g',
            #        'relative': False,
            #
            #        'font': {'size': 15}},
            number={'font': {'size': 20}, },
            domain={'y': [0, 1], 'x': [0, 1]})],
        'layout': go.Layout(
                title={'text': '%Fail',
                       'y': 1,
                       'x': 0.5,
                       'xanchor': 'center',
                       'yanchor': 'top'},
                font=dict(color='#e55467'),
                paper_bgcolor='#1f2c56',
                plot_bgcolor='#1f2c56',
                height=50
                ), }, {
        'data': [go.Indicator(
            mode='number',
            value=value_confirmed_dpt,
            # delta={'reference': delta_confirmed,
            #        'position': 'right',
            #        'valueformat': ',g',
            #        'relative': False,
            #
            #        'font': {'size': 15}},
            number={'font': {'size': 20}, },
            domain={'y': [0, 1], 'x': [0, 1]})],
        'layout': go.Layout(
                title={'text': 'DPT',
                       'y': 1,
                       'x': 0.5,
                       'xanchor': 'center',
                       'yanchor': 'top'},
                font=dict(color='aqua'),
                paper_bgcolor='#1f2c56',
                plot_bgcolor='#1f2c56',
                height=50
                ), }


@callback(
    [Output(component_id='tested_value_f1', component_property='children'),
     Output(component_id='pass_value_f1', component_property='children'),
     Output(component_id='fail_value_f1', component_property='children'),
     Output(component_id='fty_value_f1', component_property='children'),
     Output(component_id='dpt_value_f1', component_property='children')],
    [Input(component_id='Product_f1', component_property='value'),
     Input(component_id='Part_no_f1', component_property='value'),
     Input(component_id='Month_f1', component_property='value'),
     # Input(component_id='interval_db', component_property='n_intervals')
     ])
def test_count_f1(product, part_no, month):
    total = sql_data("card_total_f1")  # for total
    month_wise = sql_data("card_month_f1")  # month vise card
    part_code_wise = sql_data("card_part_f1")  # for part code data

    if product is None:
        if month is None or len(month) == 0:
            if part_no == 'all_values':
                tested_value = total['TEST_QUANTITY'].sum()
                pass_value = total['PASS_QUANTITY'].sum()
                fail_value = total['REJECT_QUANTITY'].sum()
                fty_value = str(round(((pass_value / tested_value) * 100), 1)) + '%'
                dpt_value = str(int(round(((fail_value / tested_value) * 1000), 0)))
                # return tested_value, pass_value, fail_value, fty_value
            else:
                tested_value = part_code_wise.loc[part_code_wise['PART_CODE'] == part_no]['TEST_QUANTITY'].sum()
                pass_value = part_code_wise.loc[part_code_wise['PART_CODE'] == part_no]['PASS_QUANTITY'].sum()
                fail_value = part_code_wise.loc[part_code_wise['PART_CODE'] == part_no]['REJECT_QUANTITY'].sum()
                fty_value = str(round(((pass_value / tested_value) * 100), 1)) + '%'
                dpt_value = str(int(round(((fail_value / tested_value) * 1000), 0)))
                # return tested_value, pass_value, fail_value, fty_value
        else:
            # print("month is not none")
            # print(len(month))
            if part_no == 'all_values':
                tested_value = month_wise.loc[month_wise['MONTH'].isin(month)]['TEST_QUANTITY'].sum()
                pass_value = month_wise.loc[month_wise['MONTH'].isin(month)]['PASS_QUANTITY'].sum()
                fail_value = month_wise.loc[month_wise['MONTH'].isin(month)]['REJECT_QUANTITY'].sum()
                fty_value = str(round(((pass_value / tested_value) * 100), 1)) + '%'
                dpt_value = str(int(round(((fail_value / tested_value) * 1000), 0)))
                # return tested_value, pass_value, fail_value, fty_value
            else:
                specific = part_code_wise.loc[part_code_wise['MONTH'].isin(month)]
                tested_value = specific.loc[specific['PART_CODE'] == part_no]['TEST_QUANTITY'].sum()
                pass_value = specific.loc[specific['PART_CODE'] == part_no]['PASS_QUANTITY'].sum()
                fail_value = specific.loc[specific['PART_CODE'] == part_no]['REJECT_QUANTITY'].sum()
                fty_value = str(round(((pass_value / tested_value) * 100), 1)) + '%'
                dpt_value = str(int(round(((fail_value / tested_value) * 1000), 0)))
                # return tested_value, pass_value, fail_value, fty_value
    else:
        if month is None or len(month) == 0:
            if part_no == 'all_values':
                tested_value = total['TEST_QUANTITY'].loc[product]
                pass_value = total['PASS_QUANTITY'].loc[product]
                fail_value = total['REJECT_QUANTITY'].loc[product]
                fty_value = str(round(((pass_value / tested_value) * 100), 1)) + '%'
                dpt_value = str(int(round(((fail_value / tested_value) * 1000), 0)))
                # return tested_value, pass_value, fail_value, fty_value
            else:
                specific = part_code_wise.loc[part_code_wise['PRODUCT'] == product]
                tested_value = specific.loc[specific['PART_CODE'] == part_no]['TEST_QUANTITY'].sum()
                pass_value = specific.loc[specific['PART_CODE'] == part_no]['PASS_QUANTITY'].sum()
                fail_value = specific.loc[specific['PART_CODE'] == part_no]['REJECT_QUANTITY'].sum()
                fty_value = str(round(((pass_value / tested_value) * 100), 1)) + '%'
                dpt_value = str(int(round(((fail_value / tested_value) * 1000), 0)))
                # return tested_value, pass_value, fail_value, fty_value
        else:
            month_check = month_wise.loc[month_wise['MONTH'].isin(month)]
            if product in month_check["TEST_QUANTITY"]:
                if part_no == 'all_values':
                    a = month_wise.loc[month_wise['MONTH'].isin(month)]
                    tested_value = a['TEST_QUANTITY'].loc[product]
                    pass_value = a['PASS_QUANTITY'].loc[product]
                    fail_value = a['REJECT_QUANTITY'].loc[product]
                    fty_value = str(round(((pass_value / tested_value) * 100), 1)) + '%'
                    dpt_value = str(int(round(((fail_value / tested_value) * 1000), 0)))
                    # return tested_value, pass_value, fail_value, fty_value
                else:
                    specific = part_code_wise.loc[part_code_wise['PRODUCT'] == product]
                    filtered = specific.loc[specific['MONTH'].isin(month)]
                    tested_value = filtered.loc[filtered['PART_CODE'] == part_no]['TEST_QUANTITY'].sum()
                    pass_value = filtered.loc[filtered['PART_CODE'] == part_no]['PASS_QUANTITY'].sum()
                    fail_value = filtered.loc[filtered['PART_CODE'] == part_no]['REJECT_QUANTITY'].sum()
                    fty_value = str(round(((pass_value / tested_value) * 100), 1)) + '%'
                    dpt_value = str(int(round(((fail_value / tested_value) * 1000), 0)))
                    # return tested_value, pass_value, fail_value, fty_value
            else:
                tested_value = 0
                pass_value = 0
                fail_value = 0
                fty_value = 0
                dpt_value = 0

    return tested_value, pass_value, fail_value, fty_value, dpt_value


@callback(Output(component_id='pie_chart2', component_property='figure'),
          [Input(component_id='Product_f1', component_property='value'),
           Input(component_id='Part_no_f1', component_property='value'),
           Input(component_id='Month_f1', component_property='value'),
           # Input(component_id='interval_db', component_property='n_intervals')
           ])
def pie_chart2(product, part_no, month):
    filtered_df = sql_data("raw_f1")
    if product is None:
        if month is None or len(month) == 0:
            if part_no == 'all_values':
                pie_df = filtered_df
                a = str(pie_df["FAULT_OBSERVED"].count())
                b = 'PCAs Faults Data'
                fig = px.pie(pie_df, names='PRODUCT_NAME', title=b, hole=0.3)
                fig.update_layout(title_font_size=20, title_pad_b=0, title_y=0.96)
                fig.update_traces(hovertemplate="Product:%{label} <br>Fault_Count:%{value} "
                                                "<br>Percentage: %{percent}",
                                  insidetextfont_color='white', textposition='inside')
                # fig.update_traces(textinfo='percent+value', insidetextfont_color='black')
                fig.add_annotation(x=0.5, y=0.5, text=a, font=dict(size=14, family='Verdana', color='white'),
                                   showarrow=False)
                fig.update_layout(margin=dict(b=10), plot_bgcolor='#1f2c56', paper_bgcolor='#1f2c56',
                                  font_color='white', showlegend=False, uniformtext_minsize=12, uniformtext_mode='hide')
                return fig
            else:
                pie_df = filtered_df.loc[filtered_df['PART_CODE'] == part_no]
                a = str(pie_df["FAULT_OBSERVED"].count())
                b = 'PCA Faults Data for '+part_no
                fig = px.pie(pie_df, names='PRODUCT_NAME', title=b, hole=0.3)
                fig.update_layout(title_font_size=20, title_pad_b=0, title_y=0.96)
                fig.update_traces(hovertemplate="Product:%{label} <br>Fault_Count:%{value} <br>Percentage: %{percent}",
                                  insidetextfont_color='white', textposition='inside')
                # fig.update_traces(textinfo='percent+value', insidetextfont_color='black')
                fig.add_annotation(x=0.5, y=0.5, text=a, font=dict(size=14, family='Verdana', color='white'),
                                   showarrow=False)
                fig.update_layout(margin=dict(b=10), plot_bgcolor='#1f2c56', paper_bgcolor='#1f2c56',
                                  font_color='white', showlegend=False, uniformtext_minsize=12, uniformtext_mode='hide')
                return fig
        else:
            if part_no == 'all_values':
                pie_df = filtered_df.loc[filtered_df['MONTH'].isin(month)]
                a = str(pie_df["FAULT_OBSERVED"].count())
                month_name = ",".join(month)
                b = 'PCA Faults Data for ' + month_name
                fig = px.pie(pie_df, names='PRODUCT_NAME', title=b, hole=0.3)
                fig.update_layout(title_font_size=20, title_pad_b=0, title_y=0.96)
                fig.update_traces(hovertemplate="Product:%{label} <br>Fault_Count:%{value} <br>Percentage: %{percent}",
                                  insidetextfont_color='white', textposition='inside')
                # fig.update_traces(textinfo='percent+value', insidetextfont_color='black')
                fig.add_annotation(x=0.5, y=0.5, text=a, font=dict(size=14, family='Verdana', color='white'),
                                   showarrow=False)
                fig.update_layout(margin=dict(b=10), plot_bgcolor='#1f2c56', paper_bgcolor='#1f2c56',
                                  font_color='white', showlegend=False, uniformtext_minsize=12, uniformtext_mode='hide')
                return fig
            else:
                df_month = filtered_df.loc[filtered_df['MONTH'].isin(month)]
                pie_df = df_month.loc[df_month['PART_CODE'] == part_no]
                a = str(pie_df["FAULT_OBSERVED"].count())
                b = 'PCA Faults Data for '+part_no
                fig = px.pie(pie_df, names='PRODUCT_NAME', title=b, hole=0.3)
                fig.update_layout(title_font_size=20, title_pad_b=0, title_y=0.96)
                fig.update_traces(hovertemplate="Product:%{label} <br>Fault_Count:%{value} <br>Percentage: %{percent}",
                                  insidetextfont_color='white', textposition='inside')
                # fig.update_traces(textinfo='percent+value', insidetextfont_color='black')
                fig.add_annotation(x=0.5, y=0.5, text=a, font=dict(size=14, family='Verdana', color='white'),
                                   showarrow=False)
                fig.update_layout(margin=dict(b=10), plot_bgcolor='#1f2c56', paper_bgcolor='#1f2c56',
                                  font_color='white', showlegend=False, uniformtext_minsize=12, uniformtext_mode='hide')
                return fig

    else:
        specific_df = filtered_df.loc[filtered_df['PRODUCT_NAME'] == product]
        if month is None or len(month) == 0:
            if part_no == 'all_values':
                pie_df = specific_df
                a = str(pie_df["FAULT_OBSERVED"].count())
                b = 'Total Failure for ' + product
            else:
                pie_df = specific_df.loc[specific_df['PART_CODE'] == part_no]
                a = str(pie_df["FAULT_OBSERVED"].count())
                b = 'PCA Faults Data for '+part_no

        else:
            if part_no == 'all_values':
                pie_df = specific_df.loc[specific_df['MONTH'].isin(month)]
                # return the outcomes piechart for a selected month
                a = str(pie_df["FAULT_OBSERVED"].count())
                month_name = ",".join(month)
                b = product + ' Failure for ' + month_name
            else:
                df_month = specific_df.loc[specific_df['MONTH'].isin(month)]
                pie_df = df_month.loc[df_month['PART_CODE'] == part_no]
                a = str(pie_df["FAULT_OBSERVED"].count())
                b = 'PCA Faults Data for '+part_no

    fig = px.pie(pie_df, names='FAULT_OBSERVED', title=b, hole=0.3)
    fig.update_layout(title_font_size=20, title_pad_b=0, title_y=0.96)
    fig.update_traces(hovertemplate="Fault:%{label} <br>Count:%{value} <br>Percentage: %{percent}",
                      insidetextfont_color='white', textposition='inside')
    fig.add_annotation(x=0.5, y=0.5, text=a, font=dict(size=14, family='Verdana', color='white'),
                       showarrow=False)
    fig.update_layout(margin=dict(b=10), plot_bgcolor='#1f2c56', paper_bgcolor='#1f2c56',
                      font_color='white', showlegend=False, uniformtext_minsize=12, uniformtext_mode='hide')
    return fig


@callback(Output(component_id='Bar2', component_property='figure'),
          [Input(component_id='Product_f1', component_property='value'),
           Input(component_id='Part_no_f1', component_property='value'),
           Input(component_id='Month_f1', component_property='value'),
           # Input(component_id='interval_db', component_property='n_intervals')
           ])
def bar_chart2(product, part_no, month):
    filtered_df = sql_data("raw_f1")
    map_1 = {'(?)': 'rgb(128, 177, 211)', 'ATS': '#00CC96', 'Initial': 'rgb(36, 121, 108)', 'Burn In': 'red',
             'Testing': '#A000ff', 'Pre Initial': '#00ff4f', 'Rack testing': '#Ffe200', 'ATE': '#00CC96',
             'TESTING': '#A000ff'}
    if product is None:
        if month is None or len(month) == 0:
            if part_no == 'all_values':
                d = filtered_df
            else:
                d = filtered_df.loc[filtered_df['PART_CODE'] == part_no]
        else:
            if part_no == 'all_values':
                d = filtered_df.loc[filtered_df['MONTH'].isin(month)]
            else:
                a = filtered_df.loc[filtered_df['MONTH'].isin(month)]
                d = a.loc[a['PART_CODE'] == part_no]
    else:
        specific_df = filtered_df.loc[filtered_df['PRODUCT_NAME'] == product]
        if month is None or len(month) == 0:
            if part_no == 'all_values':
                d = specific_df
            else:
                d = specific_df.loc[specific_df['PART_CODE'] == part_no]
        else:
            if part_no == 'all_values':
                d = specific_df.loc[specific_df['MONTH'].isin(month)]
            else:
                a = specific_df.loc[specific_df['MONTH'].isin(month)]
                d = a.loc[a['PART_CODE'] == part_no]

    # bar_1 = d.groupby(['FAULT_OBSERVED', 'STAGE'])['TOTAL'].size().reset_index()
    # df_sorted = bar_1.sort_values('TOTAL', ascending=False)
    # bar = df_sorted.head(20)
    bar_1 = d.groupby(['FAULT_OBSERVED', 'STAGE'])['TOTAL'].size().reset_index()
    bar_1['Percentage'] = bar_1['TOTAL'] / bar_1['TOTAL'].sum() * 100
    bar_top20 = d.groupby('FAULT_OBSERVED')['TOTAL'].size().nlargest(20).reset_index()
    bar_2 = bar_1[bar_1['FAULT_OBSERVED'].isin(bar_top20['FAULT_OBSERVED'])]
    bar = bar_2.sort_values('TOTAL', ascending=False)

    # print(df_top_10)
    fig = px.bar(bar, x='TOTAL', y='FAULT_OBSERVED', title="Faults Type", color='FAULT_OBSERVED', text='TOTAL',
                 color_discrete_map=map_1, custom_data=['STAGE', 'FAULT_OBSERVED', 'Percentage'])
    shortened_labels = [label[:25] + '...' if len(label) > 25 else label for label in bar['FAULT_OBSERVED']]
    hovertemplate = '<b>%{customdata[1]}<br>Fault_Count: %{x}<br>Fault_Percent: %{customdata[2]:.2f}%' \
                    '<br>STAGE: %{customdata[0]}'
    fig.update_traces(hovertemplate=hovertemplate)
    fig.update_layout(yaxis={'ticktext': shortened_labels, 'tickvals': bar['FAULT_OBSERVED']})
    fig.update_layout(title_font_size=20, title_pad_b=0, title_y=0.96)
    fig.update_traces(textfont_size=14, textangle=0, textposition="inside", cliponaxis=False,
                      insidetextfont_color='white')
    fig.update_layout(margin=dict(b=10), plot_bgcolor='#1f2c56', paper_bgcolor='#1f2c56',
                      font_color='white',showlegend=False)
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})  # for sorting the data in descending order
    return fig


# @callback(Output(component_id='Product_f1', component_property='options'),
#           [Input(component_id='Month_f1', component_property='value'),
#           # Input(component_id='interval_db', component_property='n_intervals')
#            ])
# def dropdown_faults_f1(month):
#     # modules = ['2KW SMR', '3KW SMR', '4KW SMR', 'SMR_2KW_SOLAR', 'SMR_3KW_SOLAR', 'CHARGER', 'M1000', 'M2000',
#     # 'WCBMS', 'SMR_1.1KW', 'CHARGER_1.1KW']
#     df_raw1 = sql_data("card_f1")
#     # filtered_df = df_raw2.loc[df_raw2['PRODUCT_NAME'].isin(modules)]
#     filtered_df = df_raw1
#     if month is None or len(month) == 0:
#         d = filtered_df
#     else:
#         d = filtered_df.loc[filtered_df['MONTH'].isin(month)]
#     return [{"label": j, "value": j}for j in d['PRODUCT'].unique()]


@callback(Output(component_id='Product_f1', component_property='options'),
          [Input(component_id='Month_f1', component_property='value'),
           Input(component_id='Part_no_f1', component_property='value')
           ])
def dropdown_faults_f1(month, part_no):
    # modules = ['2KW SMR', '3KW SMR', '4KW SMR', 'SMR_2KW_SOLAR', 'SMR_3KW_SOLAR', 'CHARGER', 'M1000', 'M2000',
    # 'WCBMS', 'SMR_1.1KW', 'CHARGER_1.1KW']
    df_raw1 = sql_data("card_f1")
    # filtered_df = df_raw2.loc[df_raw2['PRODUCT_NAME'].isin(modules)]
    filtered_df = df_raw1
    if month is None or len(month) == 0:
        if part_no == "all_values":
            d = filtered_df
        else:
            d = filtered_df.loc[filtered_df['PART_CODE'] == part_no]
    else:
        specific = filtered_df.loc[filtered_df['MONTH'].isin(month)]
        if part_no == "all_values":
            d = specific
        else:
            d = specific.loc[specific['PART_CODE'] == part_no]

    return [{"label": j, "value": j}for j in d['PRODUCT'].unique()]


@callback(Output(component_id='Part_no_f1', component_property='options'),
          [Input(component_id='Product_f1', component_property='value'),
           Input(component_id='Month_f1', component_property='value'),
           # Input(component_id='interval_db', component_property='n_intervals')
           ])
def dropdown_part_no_f1(product, month):
    filtered_df = sql_data("card_part_f1")
    if product is None:
        if month is None or len(month) == 0:
            d = filtered_df
        else:
            d = filtered_df.loc[filtered_df['MONTH'].isin(month)]
    else:
        specific = filtered_df.loc[filtered_df['PRODUCT'] == product]
        if month is None or len(month) == 0:
            d = specific
        else:
            d = specific.loc[specific['MONTH'].isin(month)]
    return [{"label": j, "value": j} for j in d['PART_CODE'].unique()]+[{'label': 'Select all', 'value': 'all_values'}]


@callback(
    Output('Part_no_f1', 'value'),
    [Input('Part_no_f1', 'options'),
     Input('Product_f1', 'value'),
     # Input('interval_db', 'n_intervals')
     ])
def set_part_no_f1_value(available_options, product):
    if product is None:
        return available_options[-1]['value']
    else:
        return available_options[-1]['value']


@callback(Output(component_id='Month_f1', component_property='options'),
          [Input(component_id='Product_f1', component_property='value'),
           Input(component_id='Part_no_f1', component_property='value')
           ])
def dropdown_month_f1(product, part_no):
    # modules = ['2KW SMR', '3KW SMR', '4KW SMR', 'SMR_2KW_SOLAR', 'SMR_3KW_SOLAR', 'CHARGER', 'M1000', 'M2000',
    # 'WCBMS', 'SMR_1.1KW', 'CHARGER_1.1KW']
    df_card_summary = sql_data("card_f1")
    # filtered_df = df_raw2.loc[df_raw2['PRODUCT_NAME'].isin(modules)]
    filtered_df = df_card_summary
    if product is None:
        if part_no == "all_values":
            d = filtered_df
        else:
            d = filtered_df.loc[filtered_df['PART_CODE'] == part_no]
    else:
        specific = filtered_df.loc[filtered_df['PRODUCT'] == product]
        if part_no == "all_values":
            d = specific
        else:
            d = specific.loc[specific['PART_CODE'] == part_no]

    final_month_list = month_data(d)

    return [{"label": j, "value": j}for j in final_month_list]

# @callback(
#     Output('Product_f1', 'value'),
#     [Input('Product_f1', 'options'),
#      Input('Part_no_f1', 'value'),
#      # Input('interval_db', 'n_intervals')
#      ])
# def set_product_f1_value(available_options, part_no):
#     if part_no != 'all_values':
#         return available_options[-1]['value']


@callback(Output(component_id='Products', component_property='options'),
          [Input(component_id='Month', component_property='value'),
           Input(component_id='Part_no', component_property='value')
          # Input(component_id='interval_db', component_property='n_intervals')
           ])
def dropdown_faults_summary(month_summary, part_no):
    # modules = ['2KW SMR', '3KW SMR', '4KW SMR', 'SMR_2KW_SOLAR', 'SMR_3KW_SOLAR', 'CHARGER', 'M1000', 'M2000',
    # 'WCBMS', 'SMR_1.1KW', 'CHARGER_1.1KW']
    df_raw1 = sql_data("card")
    # filtered_df = df_raw2.loc[df_raw2['PRODUCT_NAME'].isin(modules)]
    filtered_df = df_raw1
    if month_summary is None or len(month_summary) == 0:
        if part_no == "all_values":
            d = filtered_df
        else:
            d = filtered_df.loc[filtered_df['PART_CODE'] == part_no]
    else:
        specific = filtered_df.loc[filtered_df['MONTH'].isin(month_summary)]
        if part_no == "all_values":
            d = specific
        else:
            d = specific.loc[specific['PART_CODE'] == part_no]

    return [{"label": j, "value": j} for j in d['PRODUCT'].unique()]


# @callback(Output(component_id='Month_f1', component_property='options'),
#           [Input(component_id='Product_f1', component_property='value'),
#            Input(component_id='Part_no_f1', component_property='value')
#            ])
# def dropdown_month_f1(product, part_no):
#     # modules = ['2KW SMR', '3KW SMR', '4KW SMR', 'SMR_2KW_SOLAR', 'SMR_3KW_SOLAR', 'CHARGER', 'M1000', 'M2000',
#     # 'WCBMS', 'SMR_1.1KW', 'CHARGER_1.1KW']
#     df_card_summary = sql_data("card_f1")
#     # filtered_df = df_raw2.loc[df_raw2['PRODUCT_NAME'].isin(modules)]
#     filtered_df = df_card_summary
#     if product is None:
#         if part_no == "all_values":
#             d = filtered_df
#         else:
#             d = filtered_df.loc[filtered_df['PART_CODE'] == part_no]
#     else:
#         specific = filtered_df.loc[filtered_df['PRODUCT'] == product]
#         if part_no == "all_values":
#             d = specific
#         else:
#             d = specific.loc[specific['PART_CODE'] == part_no]
#
#     final_month_list = month_data(d)
#
#     return [{"label": j, "value": j}for j in final_month_list]


@callback(Output(component_id='Month_table', component_property='options'),
          [Input(component_id='Products_table', component_property='value'),
           ])
def dropdown_month_table(product):
    # modules = ['2KW SMR', '3KW SMR', '4KW SMR', 'SMR_2KW_SOLAR', 'SMR_3KW_SOLAR', 'CHARGER', 'M1000', 'M2000',
    # 'WCBMS', 'SMR_1.1KW', 'CHARGER_1.1KW']
    df_card_summary = sql_data("raw")
    # filtered_df = df_raw2.loc[df_raw2['PRODUCT_NAME'].isin(modules)]
    filtered_df = df_card_summary
    if product is None:
        d = filtered_df
    else:
        specific = filtered_df.loc[filtered_df['PRODUCT_NAME'] == product]
        d = specific

    final_month_list = month_data(d)

    return [{"label": j, "value": j}for j in final_month_list]


@callback(Output(component_id='Products_table', component_property='options'),
          [Input(component_id='Month_table', component_property='value'),
          # Input(component_id='interval_db', component_property='n_intervals')
           ])
def dropdown_product_table(month_table):
    # modules = ['2KW SMR', '3KW SMR', '4KW SMR', 'SMR_2KW_SOLAR', 'SMR_3KW_SOLAR', 'CHARGER', 'M1000', 'M2000',
    #            'WCBMS','2KW SUN MOBILITY', 'SMR_1.1KW', 'CHARGER_1.1KW']
    df_raw2 = sql_data("raw")
    # filtered_df = df_raw2.loc[df_raw2['PRODUCT'].isin(modules)]
    filtered_df = df_raw2
    if month_table is None or len(month_table) == 0:
        d = filtered_df
    else:
        specific = filtered_df.loc[filtered_df['MONTH'].isin(month_table)]
        d = specific

    return [{"label": j, "value": j}for j in d['PRODUCT_NAME'].unique()]


@callback(Output(component_id='Product_comparison', component_property='options'),
          [Input(component_id='Month2', component_property='value'),
          # Input(component_id='interval_db', component_property='n_intervals')
           ])
def dropdown_product_comp(month):
    df_raw2 = sql_data("raw")
    # filtered_df = df_raw2.loc[df_raw2['PRODUCT'].isin(modules)]
    filtered_df = df_raw2
    if month is None or len(month) == 0:
        d = filtered_df
    else:
        specific = filtered_df.loc[filtered_df['MONTH'] == month]
        d = specific

    return [{"label": j, "value": j}for j in d['PRODUCT_NAME'].unique()]


@callback([Output(component_id='Month2', component_property='options'),
           Output(component_id='Month1', component_property='options')],
          [Input(component_id='Product_comparison', component_property='value'),
           ])
def dropdown_month_comp(product):
    # modules = ['2KW SMR', '3KW SMR', '4KW SMR', 'SMR_2KW_SOLAR', 'SMR_3KW_SOLAR', 'CHARGER', 'M1000', 'M2000',
    # 'WCBMS', 'SMR_1.1KW', 'CHARGER_1.1KW']
    df_card_summary = sql_data("raw")
    # filtered_df = df_raw2.loc[df_raw2['PRODUCT_NAME'].isin(modules)]
    filtered_df = df_card_summary
    if product is None:
        d = filtered_df
    else:
        specific = filtered_df.loc[filtered_df['PRODUCT_NAME'] == product]
        d = specific

    final_month_list = month_data(d)

    return [{"label": j, "value": j}for j in final_month_list],\
           [{'label': i, 'value': i}for i in final_month_list] + \
           [{'label': 'Select all', 'value': 'all_values'}]


@callback([Output(component_id='comparison', component_property='children'),
           Output(component_id='bar_comparison', component_property='figure')],
          [Input(component_id='Product_comparison', component_property='value'),
           Input(component_id='Month1', component_property='value'),
           Input(component_id='Month2', component_property='value'),
           # Input(component_id='interval_db', component_property='n_intervals')
           ])
def comparison(product, month1, month2):
    filtered = df
    total = sql_data("card_total")  # for total
    month_wise = sql_data("card_month")  # month vise card
    # part_code_wise = sql_data("card_part")  # for part code data
    a = pd.DataFrame()
    fig = {}
    if product is None:
        if month1 is not None and month1 != 'all_values':
            tested_value = month_wise.loc[month_wise['MONTH'] == month1]['TEST_QUANTITY'].sum()
            month1_data = filtered.loc[filtered['MONTH'] == month1]
            # print(df_remarks)
            data1_count = month1_data['FAULT_OBSERVED'].value_counts(dropna=False)
            # percentage = month1_data['FAULT_OBSERVED'].value_counts(dropna=False, normalize=True).mul(100)\
            #                                           .round(1).astype(str) + '%'
            # column_name1 = month1 + '%'
            dpt = (round(((data1_count / tested_value)*1000), 0))
            # print(tested_value)
            column_name1 = month1 + " DPT"
            data1 = pd.concat([data1_count, dpt], axis=1, keys=[month1, column_name1])\
                .rename_axis('FAULT_OBSERVED').reset_index()

            if month2 is None:
                df_remarks = remarks(month1_data)
                d = pd.merge(data1, df_remarks, on="FAULT_OBSERVED")
                bar = d
                # print(a)
                a = bar.head(20)
                # print(bar)
                fig = go.Figure(data=[go.Bar(y=a['FAULT_OBSERVED'], x=a[month1], name=month1, text=a[month1],
                                             orientation='h')])
                fig.update_layout(barmode='group')
                fig.update_traces(textfont_size=16, textangle=0, textposition="outside", cliponaxis=False,
                                  insidetextfont_color='black')
                fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            else:
                tested_value_2 = month_wise.loc[month_wise['MONTH'] == month2]['TEST_QUANTITY'].sum()
                month2_data = filtered.loc[filtered['MONTH'] == month2]
                data2_count = month2_data['FAULT_OBSERVED'].value_counts(dropna=False)
                # percentage = month2_data['FAULT_OBSERVED'].value_counts(dropna=False, normalize=True).mul(100)\
                #                                           .round(1).astype(str) + '%'
                # column_name2 = month2+'%'
                dpt2 = (round(((data2_count / tested_value_2) * 1000), 0))
                # print(tested_value)
                column_name2 = month2 + " DPT"
                data2 = pd.concat([data2_count, dpt2], axis=1, keys=[month2, column_name2])\
                    .rename_axis('FAULT_OBSERVED').reset_index()
                df_remarks = remarks(month2_data)
                d = pd.merge(data2, df_remarks, on="FAULT_OBSERVED")
                bar = pd.merge(data1, d, how="outer", on="FAULT_OBSERVED").replace(np.NaN, 0)
                a = bar.head(20)

                fig = go.Figure(data=[go.Bar(y=a['FAULT_OBSERVED'], x=-a[month1], name=month1, text=a[month1],
                                             orientation='h'),
                                      go.Bar(y=a['FAULT_OBSERVED'], x=a[month2], name=month2, text=a[month2],
                                             orientation='h')])
                fig.update_layout(barmode='overlay')
                fig.update_traces(textfont_size=16, textangle=0, textposition="outside", cliponaxis=False,
                                  insidetextfont_color='black')
                # fig.update_layout(xaxis=dict(tickformat=',', tickvals=-a[month1],
                #                              ticktext=[val for val in a[month1]]))
                # fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        elif month1 == 'all_values':
            if month2 is None:
                month1_data = filtered
                tested_value = total['TEST_QUANTITY'].sum()
                data1_count = month1_data['FAULT_OBSERVED'].value_counts(dropna=False)
                # percentage = month1_data['FAULT_OBSERVED'].value_counts(dropna=False, normalize=True).mul(100) \
                #                                           .round(1).astype(str) + '%'
                # # data1 = month1_data.value_counts(['FAULT_OBSERVED']).reset_index(name=month1)
                # column_name1 = month1 + '%'
                dpt = (round(((data1_count / tested_value) * 1000), 0))
                # print(tested_value)
                column_name1 = month1 + " DPT"
                data1 = pd.concat([data1_count, dpt], axis=1, keys=[month1, column_name1]) \
                    .rename_axis('FAULT_OBSERVED').reset_index()
                df_remarks = remarks(month1_data)
                d = pd.merge(data1, df_remarks, on="FAULT_OBSERVED")
                # a = d
                bar = d
                # print(a)
                a = bar.head(20)
                fig = go.Figure(data=[go.Bar(y=a['FAULT_OBSERVED'], x=a[month1], name=month1, text=a[month1],
                                             orientation='h')])
                fig.update_layout(barmode='group')
                fig.update_traces(textfont_size=16, textangle=0, textposition="outside", cliponaxis=False,
                                  insidetextfont_color='black')
                fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            else:
                tested_value = month_wise.loc[month_wise['MONTH'] != month2]['TEST_QUANTITY'].sum()
                month1_data = filtered.loc[filtered['MONTH'] != month2]
                data1_count = month1_data['FAULT_OBSERVED'].value_counts(dropna=False)
                # percentage = month1_data['FAULT_OBSERVED'].value_counts(dropna=False, normalize=True).mul(100) \
                #                                           .round(1).astype(str) + '%'
                # # data1 = month1_data.value_counts(['FAULT_OBSERVED']).reset_index(name=month1)
                # column_name1 = month1 + '%'
                dpt = (round(((data1_count / tested_value) * 1000), 0))
                # print(tested_value)
                column_name1 = month1 + " DPT"
                data1 = pd.concat([data1_count, dpt], axis=1, keys=[month1, column_name1]) \
                    .rename_axis('FAULT_OBSERVED').reset_index()

                tested_value_2 = month_wise.loc[month_wise['MONTH'] == month2]['TEST_QUANTITY'].sum()
                month2_data = filtered.loc[filtered['MONTH'] == month2]
                data2_count = month2_data['FAULT_OBSERVED'].value_counts(dropna=False)
                # percentage = month2_data['FAULT_OBSERVED'].value_counts(dropna=False, normalize=True).mul(100)\
                #                                           .round(1).astype(str) + '%'
                # column_name2 = month2+'%'
                dpt2 = (round(((data2_count / tested_value_2) * 1000), 0))
                # print(tested_value)
                column_name2 = month2 + " DPT"
                data2 = pd.concat([data2_count, dpt2], axis=1, keys=[month2, column_name2])\
                    .rename_axis('FAULT_OBSERVED').reset_index()
                df_remarks = remarks(month2_data)
                d = pd.merge(data2, df_remarks, on="FAULT_OBSERVED")
                bar = pd.merge(data1, d, how="outer", on="FAULT_OBSERVED").replace(np.NaN, 0)
                a = bar.head(20)
                fig = go.Figure(data=[go.Bar(y=a['FAULT_OBSERVED'], x=-a[month1], name=month1, text=a[month1],
                                             orientation='h'),
                                      go.Bar(y=a['FAULT_OBSERVED'], x=a[month2], name=month2, text=a[month2],
                                             orientation='h')])
                fig.update_layout(barmode='overlay')
                fig.update_traces(textfont_size=16, textangle=0, textposition="outside", cliponaxis=False,
                                  insidetextfont_color='black')
                # fig.update_layout(yaxis={'categoryorder': 'total ascending'})

    else:
        specific_df = filtered.loc[filtered['PRODUCT_NAME'] == product]
        # month_check = month_wise.loc[month_wise['MONTH'] == month1]
        if month1 is not None and month1 != 'all_values':
            month_data1 = month_wise.loc[month_wise['MONTH'] == month1]
            tested_value = month_data1['TEST_QUANTITY'].loc[product]
            month1_data = specific_df.loc[specific_df['MONTH'] == month1]
            data1_count = month1_data['FAULT_OBSERVED'].value_counts(dropna=False)
            # percentage = month1_data['FAULT_OBSERVED'].value_counts(dropna=False, normalize=True).mul(100)\
            #                                           .round(1).astype(str) + '%'
            # column_name1 = month1 + '%'
            dpt = (round(((data1_count / tested_value) * 1000), 0))
            column_name1 = month1 + " DPT"
            data1 = pd.concat([data1_count, dpt], axis=1, keys=[month1, column_name1])\
                .rename_axis('FAULT_OBSERVED').reset_index()
            if month2 is None:
                df_remarks = remarks(month1_data)
                d = pd.merge(data1, df_remarks, on="FAULT_OBSERVED")
                bar = d
                # print(a)
                a = bar.head(20)
                fig = go.Figure(data=[go.Bar(y=a['FAULT_OBSERVED'], x=a[month1], name=month1, text=a[month1],
                                             orientation='h')])
                fig.update_layout(barmode='group')
                fig.update_traces(textfont_size=16, textangle=0, textposition="outside", cliponaxis=False,
                                  insidetextfont_color='black')
                fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            else:
                month_data2 = month_wise.loc[month_wise['MONTH'] == month2]
                tested_value_2 = month_data2['TEST_QUANTITY'].loc[product]
                month2_data = specific_df.loc[specific_df['MONTH'] == month2]

                data2_count = month2_data['FAULT_OBSERVED'].value_counts(dropna=False)
                # percentage = month2_data['FAULT_OBSERVED'].value_counts(dropna=False, normalize=True)\
                #                                           .mul(100).round(1).astype(str) + '%'
                # column_name2 = month2 + '%'
                dpt2 = (round(((data2_count / tested_value_2) * 1000), 0))
                column_name2 = month2 + " DPT"
                data2 = pd.concat([data2_count, dpt2], axis=1, keys=[month2, column_name2])\
                    .rename_axis('FAULT_OBSERVED').reset_index()
                df_remarks = remarks(month2_data)
                d = pd.merge(data2, df_remarks, on="FAULT_OBSERVED")
                bar = pd.merge(data1, d, how="outer", on="FAULT_OBSERVED").replace(np.NaN, 0)
                a = bar.head(20)
                fig = go.Figure(data=[go.Bar(y=a['FAULT_OBSERVED'], x=-a[month1], name=month1, text=a[month1],
                                             orientation='h'),
                                      go.Bar(y=a['FAULT_OBSERVED'], x=a[month2], name=month2, text=a[month2],
                                             orientation='h')])
                fig.update_layout(barmode='overlay')
                fig.update_traces(textfont_size=16, textangle=0, textposition="outside", cliponaxis=False,
                                  insidetextfont_color='black')
                # fig.update_layout(yaxis={'categoryorder': 'total ascending'})

        elif month1 == 'all_values':
            if month2 is None:
                tested_value = total['TEST_QUANTITY'].loc[product]
                month1_data = specific_df
                data1_count = month1_data['FAULT_OBSERVED'].value_counts(dropna=False)
                # percentage = month1_data['FAULT_OBSERVED'].value_counts(dropna=False, normalize=True).mul(100) \
                #                                           .round(1).astype(str) + '%'
                # # data1 = month1_data.value_counts(['FAULT_OBSERVED']).reset_index(name=month1)
                # column_name1 = month1 + '%'
                dpt = (round(((data1_count / tested_value) * 1000), 0))
                column_name1 = month1 + " DPT"
                data1 = pd.concat([data1_count, dpt], axis=1, keys=[month1, column_name1]) \
                    .rename_axis('FAULT_OBSERVED').reset_index()
                df_remarks = remarks(month1_data)
                d = pd.merge(data1, df_remarks, on="FAULT_OBSERVED")
                bar = d
                # print(a)
                a = bar.head(20)
                fig = go.Figure(data=[go.Bar(y=a['FAULT_OBSERVED'], x=a[month1], name=month1, text=a[month1],
                                             orientation='h')])
                fig.update_layout(barmode='group')
                fig.update_traces(textfont_size=16, textangle=0, textposition="outside", cliponaxis=False,
                                  insidetextfont_color='black')
                fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            else:
                month_data1 = month_wise.loc[month_wise['MONTH'] != month2]
                # tested_value = month_data1.loc[month_data1['PRODUCT'] == product]['TEST_QUANTITY'].sum()
                tested_value = month_data1['TEST_QUANTITY'].loc[product].sum()
                month1_data = specific_df.loc[specific_df['MONTH'] != month2]
                data1_count = month1_data['FAULT_OBSERVED'].value_counts(dropna=False)
                # percentage = month1_data['FAULT_OBSERVED'].value_counts(dropna=False, normalize=True).mul(100) \
                #                                           .round(1).astype(str) + '%'
                # # data1 = month1_data.value_counts(['FAULT_OBSERVED']).reset_index(name=month1)
                # column_name1 = month1 + '%'
                dpt = (round(((data1_count / tested_value) * 1000), 0))
                column_name1 = month1 + " DPT"
                data1 = pd.concat([data1_count, dpt], axis=1, keys=[month1, column_name1])\
                    .rename_axis('FAULT_OBSERVED').reset_index()

                month_data2 = month_wise.loc[month_wise['MONTH'] == month2]
                tested_value_2 = month_data2['TEST_QUANTITY'].loc[product]
                month2_data = specific_df.loc[specific_df['MONTH'] == month2]
                data2_count = month2_data['FAULT_OBSERVED'].value_counts(dropna=False)
                # percentage = month2_data['FAULT_OBSERVED'].value_counts(dropna=False, normalize=True).mul(100)\
                #                                           .round(1).astype(str) + '%'
                # column_name2 = month2+'%'
                dpt2 = (round(((data2_count / tested_value_2) * 1000), 0))
                column_name2 = month2 + " DPT"
                data2 = pd.concat([data2_count, dpt2], axis=1, keys=[month2, column_name2])\
                    .rename_axis('FAULT_OBSERVED').reset_index()
                df_remarks = remarks(month2_data)
                d = pd.merge(data2, df_remarks, on="FAULT_OBSERVED")
                bar = pd.merge(data1, d, how="outer", on="FAULT_OBSERVED").replace(np.NaN, 0)
                a = bar.head(20)
                fig = go.Figure(data=[go.Bar(y=a['FAULT_OBSERVED'], x=-a[month1], name=month1, text=a[month1],
                                             orientation='h'),
                                      go.Bar(y=a['FAULT_OBSERVED'], x=a[month2], name=month2, text=a[month2],
                                             orientation='h')])
                fig.update_layout(barmode='overlay')
                fig.update_traces(textfont_size=16, textangle=0, textposition="outside", cliponaxis=False,
                                  insidetextfont_color='black')
                # fig.update_layout(yaxis={'categoryorder': 'total ascending'})

    return html.Div([dash_table.DataTable(data=bar.to_dict('records'),
                                          columns=[{'name': j, 'id': j} for j in a.columns],
                                          editable=True,
                                          filter_action="native",
                                          sort_action="native",
                                          sort_mode='multi',
                                          fixed_rows={'headers': True},
                                          style_header={'backgroundColor': "rgb(50, 50, 50)",
                                                        'color': 'white',
                                                        'fontWeight': 'bold',
                                                        'textAlign': 'center', },
                                          # style_header={'backgroundColor': "#FFD700",
                                          #               'fontWeight': 'bold',
                                          #               'textAlign': 'center', },
                                          style_table={'height': 420, 'overflowX': 'scroll'},
                                          style_cell={'minWidth': '130px', 'width': '140px',
                                                      'maxWidth': '130px', 'whiteSpace': 'normal',
                                                      'textAlign': 'center',
                                                      'backgroundColor': 'white', 'color': 'black'},
                                          style_data_conditional=colour_condition(a)
                                          # [
                                          #     {
                                          #         'if': {
                                          #             'filter_query': '{{{column1}}} > {{{column2}}}'.format(
                                          #                 column1=month1, column2=month2),
                                          #             'column_id': month2
                                          #         },
                                          #         'backgroundColor': '#3D9970',
                                          #         'color': 'white'
                                          #     }, {
                                          #         'if': {
                                          #             'filter_query': '{{{column1}}} < {{{column2}}}'.format(
                                          #                 column1=month1, column2=month2),
                                          #             'column_id': month2
                                          #         },
                                          #         'backgroundColor': 'tomato',
                                          #         'color': 'white'
                                          #     }
                                          # ]

                                          # style_data_conditional=(
                                          #     [
                                          #         {'if': {'row_index': x, 'column_id': month1},
                                          #          'background-color': 'tomato', 'color': 'white'}
                                          #         for x in a[a[month1] > 15].index
                                          #
                                          #         # {{'if': {'row_index': x, 'column_id': month2},
                                          #         #  'background-color': 'tomato', 'color': 'white'}
                                          #         # for x in a[a[month2] > 15].index
                                          #         #
                                          #         # }
                                          #         # {
                                          #         #     'if': {
                                          #         #         'filter_query': '{} > 15'.format(month2),
                                          #         #         'column_id': month2,
                                          #         #
                                          #         #     },
                                          #         #     'backgroundColor': 'tomato',
                                          #         #     'color': 'white'
                                          #         # },
                                          #     ]),
                                          ),
                     html.Hr()
                     ]), fig


@callback(
    [Output(component_id='tested_all', component_property='children'),
     Output(component_id='pass_all', component_property='children'),
     Output(component_id='fail_all', component_property='children'),
     Output(component_id='fty_all', component_property='children'),
     Output(component_id='dpt_all', component_property='children')],
    [Input(component_id='Product_all', component_property='value'),
     # Input(component_id='Part_no', component_property='value'),
     Input(component_id='Month_all', component_property='value'),
     # Input(component_id='interval_db', component_property='n_intervals')
     ])
def test_count(product, month):
    total = sql_data("card_total")  # for total
    month_wise = sql_data("card_month")  # month vise card
    part_code_wise = sql_data("card_part")  # for part code data

    if product is None:
        if month is None or len(month) == 0:
            tested_value = total['TEST_QUANTITY'].sum()
            pass_value = total['PASS_QUANTITY'].sum()
            fail_value = total['REJECT_QUANTITY'].sum()
            fty_value = str(round(((pass_value / tested_value) * 100), 1)) + '%'
            dpt_value = str(int(round(((fail_value / tested_value) * 1000), 0)))
            # return tested_value, pass_value, fail_value, fty_value
        else:
            tested_value = month_wise.loc[month_wise['MONTH'].isin(month)]['TEST_QUANTITY'].sum()
            pass_value = month_wise.loc[month_wise['MONTH'].isin(month)]['PASS_QUANTITY'].sum()
            fail_value = month_wise.loc[month_wise['MONTH'].isin(month)]['REJECT_QUANTITY'].sum()
            fty_value = str(round(((pass_value / tested_value) * 100), 1)) + '%'
            dpt_value = str(int(round(((fail_value / tested_value) * 1000), 0)))
    else:
        if month is None or len(month) == 0:
            # print(total)
            # a = total.loc[total['']]
            tested_value = total['TEST_QUANTITY'].loc[product].sum()
            pass_value = total['PASS_QUANTITY'].loc[product].sum()
            fail_value = total['REJECT_QUANTITY'].loc[product].sum()
            fty_value = str(round(((pass_value / tested_value) * 100), 1)) + '%'
            dpt_value = str(int(round(((fail_value / tested_value) * 1000), 0)))
            # return tested_value, pass_value, fail_value, fty_value
        else:
            month_check = month_wise.loc[month_wise['MONTH'].isin(month)]
            # if product in month_check["TEST_QUANTITY"]:
            if month_check["TEST_QUANTITY"].isin(product).any():
                a = month_wise.loc[month_wise['MONTH'].isin(month)]
                tested_value = a['TEST_QUANTITY'].loc[product].sum()
                pass_value = a['PASS_QUANTITY'].loc[product].sum()
                fail_value = a['REJECT_QUANTITY'].loc[product].sum()
                fty_value = str(round(((pass_value / tested_value) * 100), 1)) + '%'
                dpt_value = str(int(round(((fail_value / tested_value) * 1000), 0)))
                # return tested_value, pass_value, fail_value, fty_value
            else:
                tested_value = 0
                pass_value = 0
                fail_value = 0
                fty_value = 0
                dpt_value = 0

    return tested_value, pass_value, fail_value, fty_value, dpt_value


@callback(Output(component_id='Product_all', component_property='options'),
          [Input(component_id='Month_all', component_property='value'),
           # Input(component_id='Part_no', component_property='value')
          # Input(component_id='interval_db', component_property='n_intervals')
           ])
def dropdown_product_all(month_summary):
    # modules = ['2KW SMR', '3KW SMR', '4KW SMR', 'SMR_2KW_SOLAR', 'SMR_3KW_SOLAR', 'CHARGER', 'M1000', 'M2000',
    # 'WCBMS', 'SMR_1.1KW', 'CHARGER_1.1KW']
    df_raw1 = sql_data("card")
    # filtered_df = df_raw2.loc[df_raw2['PRODUCT_NAME'].isin(modules)]
    filtered_df = df_raw1

    if month_summary is None or len(month_summary) == 0:
        d = filtered_df
    else:
        specific = filtered_df.loc[filtered_df['MONTH'].isin(month_summary)]
        d = specific
    F2_NEW = ['M2000', 'WCBMS']
    return [{'label': 'F2_old', 'value': 'M1000'}, {'label': 'F2_new', 'value': ['M2000', 'WCBMS']}]
    # return [{"label": j, "value": j} for j in d['PRODUCT'].unique()]+[{'label': 'F2_old', 'value': 'M1000'}]
# 'M2000' ,'WCBMS','DCIO_F2'


@callback(Output(component_id='Month_all', component_property='options'),
          [Input(component_id='Product_all', component_property='value'),
           # Input(component_id='Part_no', component_property='value'),
           # Input(component_id='interval_db', component_property='n_intervals')
           ])
def dropdown_month(product):
    filtered_df = sql_data("card")
    if product is None:
        d = filtered_df
    else:
        specific = filtered_df.loc[filtered_df['PRODUCT'].isin(product)]
        d = specific
    final_month_list = month_data(d)

    return [{"label": j, "value": j} for j in final_month_list]

