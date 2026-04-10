from db import get_collection
import pandas as pd

def load_data():
    collection = get_collection()
    data = list(collection.find({}, {"_id": 0}))  # remove Mongo _id
    return pd.DataFrame(data)


df = load_data()

print("Data loaded from MongoDB")
print(df.head())

# Repository Age Analysis
df["created_at"] = pd.to_datetime(df["created_at"], utc=True)
df["age_days"] = (pd.Timestamp.now(tz="UTC") - df["created_at"]).dt.days

# Repository Growth Rate
df["stars_per_day"] = df["stars"] / df["age_days"]
top_growth = df.sort_values("stars_per_day", ascending=False)
print("Top Growing Repositories:")
print(top_growth[["name", "stars_per_day"]])

# Language Analysis
df["language"] = df["language"].fillna("Unknown")
lang = df.groupby("language")["stars"].mean().sort_values(ascending=False)
print("Average Stars per Language:")
print(lang)
