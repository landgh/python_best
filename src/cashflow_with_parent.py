import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_random_hierarchy(max_depth=6):
    depth = random.randint(1, max_depth)
    return '.'.join(str(random.randint(1, 9)) for _ in range(depth))

# Ensure unique hierarchies
hierarchies = set()
while len(hierarchies) < 400:
    hierarchies.add(generate_random_hierarchy())

# Create the DataFrame
df_cff = pd.DataFrame({'hierarchy': list(hierarchies)[:10]})

# Generate date columns
start_date = datetime.strptime("01-DEC-2014", "%d-%b-%Y")
date_columns = [(start_date + timedelta(days=i)).strftime("%d-%b-%Y") for i in range(250)]

# Create a dictionary to hold the amount columns
amount_columns = {date: np.round(np.random.uniform(0, 1000000000, size=len(df_cff)), 2) for date in date_columns}

# Concatenate the amount columns to the DataFrame
df_cff = pd.concat([df_cff, pd.DataFrame(amount_columns)], axis=1)

print(df_cff.shape)  # (400, 250)
print(df_cff.head())
