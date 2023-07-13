# Import required libraries
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import warnings
warnings.simplefilter(action='ignore', category=UserWarning)
pd.options.mode.chained_assignment = None

xls = pd.ExcelFile("Faults_March.xlsx", engine='openpyxl')
# to read all sheets to a map

sheet_to_df_map = {}
for sheet_name in xls.sheet_names:
    sheet_to_df_map[sheet_name] = xls.parse(sheet_name)
# sheet_to_df_map
# print(sheet_to_df_map.get("RAW"))
sheet_name_list = list(sheet_to_df_map.keys())
# print(sheet_name_list)
df_raw = sheet_to_df_map.get("RAW")
# df_raw["REPAIRING_ACTION"] = df_raw["REPAIRING_ACTION"].replace(np.nan, 'PENDING', regex=True)
# for i in range(len(df_raw)):
#     # print(df_raw.loc[i]["Repaired Date "])
#     if df_raw.iloc[i]["REPAIRING_ACTION"].upper() == "PENDING":
#         df_raw.at[i, "FAULT_CATEGORY"] = "PENDING"
#         # df_raw.at[i, "REPAIRING_DATE"] = "Pending"
#         df_raw.at[i, "KEY_COMPONENT"] = "PENDING"
#         df_raw.at[i, "POSSIBLE_REASON"] = "PENDING"
#
df_raw['TOTAL'] = 'TOTAL'
df_raw['FAULT_OBSERVED'] = df_raw['FAULT_OBSERVED'].str.upper()
#
# df_raw.loc[df_raw["STAGE"].str.contains('Test', case=False), 'STAGE'] = 'Testing'
# df_raw.loc[
#         df_raw['FAULT_CATEGORY'].str.contains('Fail|Faulty|Faulity', case=False), 'FAULT_CATEGORY'] = 'Comp. Fail'
# df_raw.loc[df_raw['FAULT_CATEGORY'].str.contains('broken|damage|dmg|miss|brake',
#                                                  case=False), 'FAULT_CATEGORY'] = 'Comp. Miss/Damage'
# df_raw.loc[df_raw['FAULT_CATEGORY'].str.contains('Shorting|Solder|short|dry',
#                                                  case=False), 'FAULT_CATEGORY'] = 'Soldering Issue'
# df_raw.loc[df_raw['FAULT_CATEGORY'].str.contains('Magnet|transformer|tfr',
#                                                  case=False), 'FAULT_CATEGORY'] = 'Magnetics Issue'
# df_raw.loc[df_raw['FAULT_CATEGORY'].str.contains('Polarity', case=False), 'FAULT_CATEGORY'] = 'Polarity'
# df_raw.loc[df_raw['FAULT_CATEGORY'].str.contains('cc |Control', case=False), 'FAULT_CATEGORY'] = 'CC Issue'
# df_raw.loc[df_raw['FAULT_CATEGORY'].str.contains('ecn', case=False), 'FAULT_CATEGORY'] = 'ECN'
# df_raw.loc[df_raw['FAULT_CATEGORY'].str.contains('scrap', case=False), 'FAULT_CATEGORY'] = 'SCRAP'
# df_raw.loc[df_raw['FAULT_CATEGORY'].str.contains('pending', case=False), 'FAULT_CATEGORY'] = 'PENDING'
#
# df_raw["PART_CODE"] = df_raw["PART_CODE"].replace('HE315441', 'HE512865', regex=True)
# df_raw["PART_CODE"] = df_raw["PART_CODE"].replace('HE315471', 'HE513140', regex=True)
# df_raw["PART_CODE"] = df_raw["PART_CODE"].replace('HE315731', 'HE513180', regex=True)
#
df = df_raw[['PRODUCT_NAME', 'PART_CODE', 'DATE', 'MONTH', 'STAGE', 'FAULT_OBSERVED', 'FAULT_CATEGORY',
             'REPAIRING_ACTION', 'KEY_COMPONENT', 'POSSIBLE_REASON']]


df = df['FAULT_OBSERVED'].apply(lambda x: x.upper())

df_card = sheet_to_df_map.get("Card")
# df_card.rename(columns=df_card.iloc[0], inplace=True)
# df_card.drop(df_card.index[0], inplace=True)

# # group by product for card
# card_product_total = df_card.groupby(['PRODUCT'])[['TEST QUANTITY', 'PASS QUANTITY', 'REJECT QUANTITY', 'FTY(%)']]
# .sum()
#
# # group by product for part code and month
# card_part_code_month = df_card.groupby(['PRODUCT', 'PART CODE', 'MONTH'])[['TEST QUANTITY', 'PASS QUANTITY',
#                                                                            'REJECT QUANTITY', 'FTY(%)']]\
#     .sum().reset_index()
#
# # group by product for month
# card_month = df_card.groupby(['PRODUCT', 'MONTH'])[['TEST QUANTITY', 'PASS QUANTITY', 'REJECT QUANTITY', 'FTY(%)']]\
#     .sum().reset_index().set_index('PRODUCT')

df_smr = sheet_to_df_map.get("SMR")
# df_smr_filter = df_smr.groupby('PRODUCT').sum()
# df_smr_month = df_smr.groupby(['PRODUCT', 'MONTH']).sum().reset_index().set_index('PRODUCT')
# df_smr_part_no = df_smr.groupby(['PRODUCT', 'MONTH', 'PART_CODE']).sum().reset_index().set_index('PRODUCT')
df_mcm = sheet_to_df_map.get("MCM")
# df_mcm_filter = df_mcm.groupby('PRODUCT').sum()
# df_mcm_month = df_mcm.groupby(['PRODUCT', 'MONTH']).sum().reset_index().set_index('PRODUCT')
# df_mcm_part_no = df_mcm.groupby(['PRODUCT', 'MONTH', 'PART_CODE']).sum().reset_index().set_index('PRODUCT')

engine = create_engine("mysql+pymysql://root:sep_2022@localhost/tarundb")
# conn = pymysql.connect(
#     host='localhost',
#     port=3306,
#     user='root',
#     passwd='sep@2022',
#     db='tarundb'
# )
# engine.execute("DROP TABLE Card_data")
# engine.execute("DROP TABLE Faults_data")
# engine.execute("DROP TABLE SMR_data")
# engine.execute("DROP TABLE MCM_data")

df_raw.to_sql("Faults_data", engine, if_exists='append', index=True, chunksize=200)
df_card.to_sql("Card_data", engine, if_exists='append', index=True, chunksize=200)
df_smr.to_sql("SMR_data", engine, if_exists='append', index=True, chunksize=200)
df_mcm.to_sql("MCM_data", engine, if_exists='append', index=True, chunksize=200)
# a = "FEB'23"
# engine.execute("DELETE FROM tarundb.faults_data WHERE MONTH='FEB'")
