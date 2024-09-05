import pandas as pd


df = pd.read_csv("injuries.csv")
# parse dates
df["Date"] = pd.to_datetime(df["Date"])
# create new injury duration column
# Dictionary to store results
results = {}

# Track the acquired dates
acquired_dates = {}

# Iterate over DataFrame rows
for index, row in df.iterrows():
    if pd.notna(row["Acquired"]):
        if row["Acquired"] != " ":  # remove empty strings
            person = row["Acquired"]
            acquired_dates[person] = row["Date"]
    if pd.notna(row["Relinquished"]):
        person = row["Relinquished"]
        if person in acquired_dates:
            acquired_date = acquired_dates.pop(person)
            Relinquished_date = row["Date"]
            if person not in results:
                results[person] = []
            results[person].append((acquired_date, Relinquished_date))

# load the results into a new DataFrame
injuries = pd.DataFrame(columns=["Person", "Acquired_date", "Relinquished_date"])
for person, dates in results.items():
    for acquired_date, Relinquished_date in dates:
        injuries = pd.concat(
            [
                injuries,
                pd.DataFrame(
                    {
                        "Person": [person],
                        "Acquired_date": [acquired_date],
                        "Relinquished_date": [Relinquished_date],
                    }
                ),
            ]
        )
# drop row with no person
injuries = injuries.dropna(subset=["Person"])
injuries.to_csv("injuries_clean.csv", index=False)
# create a new column for injury duration
injuries["Injury_duration"] = injuries["Relinquished_date"] - injuries["Acquired_date"]
# group by person and calculate the total injury duration, and the number of injuries, and average injury duration
injuries = injuries.groupby("Person").agg(
    Total_duration=("Injury_duration", "sum"),
    Number_of_injuries=("Injury_duration", "count"),
    # use median because somtimes the spider misses dates which leads to outliers
    Median_duration=("Injury_duration", "meadian"),
    # last injury date
    Last_injury_date=("Relinquished_date", "max"),
)
# express the total duration in years
injuries["Total_duration_yrs"] = injuries["Total_duration"].dt.days / 365.25
# sort  by Last_injury_date
injuries = injuries.sort_values("Last_injury_date")
print(injuries.head())
# save the results
injuries.to_csv("injuries_by_person.csv")
