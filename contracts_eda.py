"""
Do simple EDA for a multi-variable linear model between Salary and All the other variables
"""

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

# Load the data
data = pd.read_csv("players_stats.csv")

# load in the injury data and merge with the data
injury_data = pd.read_csv("injuries_by_person.csv")
# rename Person to Player
injury_data = injury_data.rename(columns={"Person": "Player"})

# merge the data on Player
data = data.merge(injury_data, on="Player", how="left")

# drop Total_duration_yrs, Total_duration, Last_injury_date
data = data.drop(columns=["Total_duration_yrs", "Total_duration", "Last_injury_date"])

# convert Average_duration "124 days 03:47:22.105263158" -> 124
data["Average_duration"] = data["Average_duration"].str.split(" ").str[0].astype(float)

print(data.info())

# drop Player and Link columns
data = data.drop(columns=["Player", "Link"])

# remove Nan values
data = data.dropna()

# "Salary" is the target variable
Y = data["Salary"]
X = data.drop(columns=["Salary"])

# NB: there is very collinearity between the variables

# create a test train split
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.1)

# fit a linear model
model = LinearRegression()
model.fit(X_train, Y_train)

# evaluate the model
score = model.score(X_test, Y_test)
print("R^2 score:", score)

# 0.83 R^2 score, not bad for a simple linear model
