import pandas
import csv

df = pandas.read_csv("SignData.csv")
print(list(df))
df = df.sort_values("SignFrequency(M)")
print(len(df['EntryID']))
a = df[["EntryID", "SignFrequency(M)", "SelectedFingers", "Flexion", "Movement"]]
a.to_csv("freq.csv", index = False)
df2 = pandas.read_csv("freq.csv")
# for index, row in df2.iterrows():
	# print row["EntryID"], row["SignFrequency(M)"], row["SelectedFingers"], row["Flexion"], row["Movement"]