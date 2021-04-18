import pandas as pd

# read in dataset
dataset = pd.read_csv("dataset.csv", header=0)

# slice out dataset and drop index and save
subset_100_df = dataset.sample(n=100)
subset_100_df.drop(subset_100_df.columns[0], axis=1)
subset_100_df.to_csv("subset_100.csv", sep=",")

# read back and verify
df = pd.read_csv("subset_100.csv", header=0)
print(df)