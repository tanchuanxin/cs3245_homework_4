import pandas as pd

# read in dataset
dataset = pd.read_csv("dataset.csv", header=0)

# slice out dataset save
subset_100_df = dataset.sample(n=100)
subset_100_df.to_csv("subset_100.csv", sep=",")

# read back and drop index and save
subset_100_df = pd.read_csv("subset_100.csv", header=0)

subset_100_df.drop(subset_100_df.columns[subset_100_df.columns.str.contains('unnamed', case = False)], axis = 1, inplace = True)
subset_100_df.to_csv("subset_100.csv", sep=",")
print(subset_100_df)