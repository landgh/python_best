import pandas as pd
import numpy as np
import random

def generate_random_hierarchy(max_depth=6):
    depth = random.randint(1, max_depth)
    return '.'.join(str(random.randint(1, 9)) for _ in range(depth))

# Ensure unique hierarchies
hierarchies = set()
while len(hierarchies) < 400:
    hierarchies.add(generate_random_hierarchy())

# Create the DataFrame
df_cff = pd.DataFrame({'hierarchy': list(hierarchies)})

# Add 249 amount columns with random float values
for i in range(1, 250):
    df_cff[f'amount_{i}'] = np.round(np.random.uniform(0, 1000000000, size=len(df_cff)), 2)

print(df_cff.shape)  # (400, 250)
print(df_cff.head())
