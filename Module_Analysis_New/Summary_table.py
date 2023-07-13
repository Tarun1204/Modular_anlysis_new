# Import required libraries
import pandas as pd
import numpy as np
import warnings

warnings.simplefilter(action='ignore', category=UserWarning)
pd.options.mode.chained_assignment = None


def table_summary(df):
    df_table = df
    df_table.loc[df_table["STAGE"].str.contains('Test', case=False), 'STAGE'] = 'Testing'
    df_table.loc[
        df_table['FAULT_CATEGORY'].str.contains('Fail|Faulty|Faulity', case=False), 'FAULT_CATEGORY'] = 'Comp. Fail'
    df_table.loc[df_table['FAULT_CATEGORY'].str.contains('broken|damage|dmg|miss|brake',
                                                         case=False), 'FAULT_CATEGORY'] = 'Comp. Miss/Damage'
    df_table.loc[df_table['FAULT_CATEGORY'].str.contains('Shorting|Solder|short|dry',
                                                         case=False), 'FAULT_CATEGORY'] = 'Soldering Issue'
    df_table.loc[df_table['FAULT_CATEGORY'].str.contains('Magnet|transformer|tfr',
                                                         case=False), 'FAULT_CATEGORY'] = 'Magnetics Issue'
    df_table.loc[df_table['FAULT_CATEGORY'].str.contains('Polarity', case=False), 'FAULT_CATEGORY'] = 'Polarity'
    df_table.loc[df_table['FAULT_CATEGORY'].str.contains('cc |Control', case=False), 'FAULT_CATEGORY'] = 'CC Issue'
    df_table.loc[df_table['FAULT_CATEGORY'].str.contains('ecn', case=False), 'FAULT_CATEGORY'] = 'ECN'
    df_table.loc[df_table['FAULT_CATEGORY'].str.contains('scrap', case=False), 'FAULT_CATEGORY'] = 'SCRAP'
    df_table.loc[df_table['FAULT_CATEGORY'].str.contains('pending', case=False), 'FAULT_CATEGORY'] = 'PENDING'

    df = df_table.groupby(["FAULT_OBSERVED"], as_index=False).count()

    # for making df with component values
    # a = lambda x: str(x.count()) + '/n ' + '(' + ', '.join(str(v) + ' : ' + str(x.value_counts()[v]) for v in
    #                                                        np.unique(x)) + ')'  # if v.count(",") < 9
    df_data = df_table.pivot_table(columns='FAULT_CATEGORY', index='FAULT_OBSERVED', values='KEY_COMPONENT',
                                   aggfunc=lambda x: str(x.count()) + '/n ' + '(' + ', '.join(str(v)+' : ' +
                                                                                              str(x.value_counts()[v])
                                                                                              for v in np.unique(x)
                                                                                              if v.count(",") < 9)+')')\
        .fillna('').reset_index()
    df_data = df_data.rename(columns={"COMPONENT DAMAGE": "Dmg", "COMPONENT MISSING": "Miss",
                                      "FAULT_OBSERVED": "Faults", "Component faulty": "faulty",
                                      "REVERSE POLARITY": "Polarity", "SOLDERING ISSUE": "Solder"})
    df_data["Faults"] = df_data["Faults"].str.capitalize()

    bar = pd.crosstab(df_table["FAULT_OBSERVED"], df_table["STAGE"])
    bar = bar.reset_index()
    bar = bar.rename(columns={"FAULT_OBSERVED": "Faults"})

    category = pd.crosstab(df_table["FAULT_OBSERVED"], df_table["FAULT_CATEGORY"])
    category = category.reset_index()
    category = category.rename(columns={"FAULT_OBSERVED": "Faults"})

    df = df.sort_values(by=['STAGE'], ascending=False)
    total_sum = df["STAGE"].sum()
    # print(total_sum)

    final_df = pd.DataFrame()
    final_df["Faults"] = df["FAULT_OBSERVED"]
    final_df.reset_index()

    for i in range(len(final_df)):
        final_df.at[i, "Total"] = str(df.at[i, "STAGE"]) + "/" + str(total_sum)

        final_df.at[i, "%age"] = str(round(float(df.at[i, "STAGE"] / total_sum) * 100, 1)) + "%"

    final_df = pd.merge(final_df, bar, how="left", on="Faults")
    final_df = pd.merge(final_df, category, how="left", on="Faults")
    # final_df = pd.merge(final_df, df_data, how="left", on="Faults")
    final_df = final_df.rename(columns={"COMPONENT DAMAGE": "Dmg",
                                        "COMPONENT MISSING": "Miss",
                                        "Component faulty": "faulty",
                                        "REVERSE POLARITY": "Polarity",
                                        "SOLDERING ISSUE": "Solder"})
    final_df["Faults"] = final_df["Faults"].str.capitalize()  # printing data in normal case
    return final_df

    # final_df
    # final_df.to_excel("Final.xlsx")
    # final_df.to_html("Final.html", index=False, justify="center")
    # print(final_df)
    # final_df
