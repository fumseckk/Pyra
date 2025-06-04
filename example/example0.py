import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

df = pd.read_csv("data.csv")
# Columns: ['Fruit', 'Amount', 'Label']
result = df.drop_duplicates(inplace=True)

plt.plot(df["Fruit"], df["Amount"])

scaler = StandardScaler()
X_scaled = scaler.fit_transform(df[["Amount"]])

X_train, X_test, y_train, y_test = train_test_split(X_scaled, df["Label"])

model = LogisticRegression()
model.fit(X_train, y_train)