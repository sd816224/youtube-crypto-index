import pandas as pd

# Assuming you have two dataframes: df1 and df2
# Both dataframes have a 'timestamp' column

merged_df = pd.merge(df1, df2, on='timestamp')
