import time
import pandas as pd
from cashflow_with_parent import df_cff

# Sample data with multiple amount columns
# data = {
#     'hierarchy': ['1', '1.2', '1.2.3', '1.2.3.4', '1.2.3.5', '2', '2.1', '2.1.1'],
#     'amount1': [0, 0, 0, 10, 20, 0, 0, 15],
#     'amount2': [5, 0, 0, 2, 3, 0, 0, 4]
# }


# df = pd.DataFrame(data)

df = df_cff

df.to_csv('synthetic_hierarchy_data.csv', index=False)


# Identify all numeric columns to roll up (excluding 'hierarchy')
amount_cols = [col for col in df.columns if col != 'hierarchy']

# Initialize a dictionary of dictionaries to store results
agg_dict = {}

start_time = time.time()

# Iterate over rows to build up sums at each parent level
for _, row in df.iterrows():
    path_parts = row['hierarchy'].split('.')
    for i in range(1, len(path_parts) + 1):
        parent_key = '.'.join(path_parts[:i])
        if parent_key not in agg_dict:
            agg_dict[parent_key] = {col: 0 for col in amount_cols}
        for col in amount_cols:
            print(f"parent_key: [{parent_key}][{col}] beginning {agg_dict[parent_key][col]}, adding row[{col}]: {row[col]}")
            agg_dict[parent_key][col] += row[col]

# Convert agg_dict into a DataFrame
agg_df = pd.DataFrame([
    {'hierarchy': key, **values} for key, values in agg_dict.items()
])

# Calculate and display elapsed time
print(f"Elapsed time: {time.time() - start_time} .................")

# Optional: sort by hierarchy level and name
agg_df['level'] = agg_df['hierarchy'].apply(lambda x: len(x.split('.')))
agg_df = agg_df.sort_values(by=['level', 'hierarchy']).drop(columns='level').reset_index(drop=True)

agg_df.to_csv('synthetic_hierarchy_data_rollup.csv', index=False)

print(agg_df)
