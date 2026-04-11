from db import get_collection
import pandas as pd
from collections import Counter

def load_data():
    collection = get_collection()
    data = list(collection.find({}, {"_id": 0}))
    return pd.DataFrame(data)


df = load_data()

print("Data loaded from MongoDB")
# print(df.head())

# Feature Engineering
df["created_at"] = pd.to_datetime(df["created_at"], utc=True)
df["updated_at"] = pd.to_datetime(df["updated_at"], utc=True)
df["age_days"] = (pd.Timestamp.now(tz="UTC") - df["created_at"]).dt.days
df["stars_per_day"] = df["stars"] / df["age_days"].replace(0, 1)

# Extract features from Contributor lists
df["contributors"] = df["contributors"].apply(lambda x: x if isinstance(x, list) else [])
df["recent_commits"] = df["recent_commits"].apply(lambda x: x if isinstance(x, list) else [])

df["contributors_count"] = df["contributors"].apply(len)
df["total_contributions"] = df["contributors"].apply(
    lambda x: sum(c.get("contributions", 0) for c in x)
)

# Extract features from commit lists
df["commit_count"] = df["recent_commits"].apply(len)

def extract_commit_dates(commits):
    dates = []
    for c in commits:
        try:
            dates.append(c["commit"]["author"]["date"])
        except:
            continue
    return dates
df["commit_dates"] = df["recent_commits"].apply(extract_commit_dates)

def compute_commit_frequency(dates):
    if len(dates) < 2:
        return 0
    dates = pd.to_datetime(dates)
    days = (max(dates) - min(dates)).days
    return len(dates) / (days if days > 0 else 1)
df["commit_frequency"] = df["commit_dates"].apply(compute_commit_frequency)

# print(df["contributors_count"])
# print(df["total_contributions"])
# print(df["commit_count"])
# print(df["commit_dates"])

#repository scoring and efficiency metrics
df["activity_score"] = (
    df["commit_count"] * 0.4 +
    df["contributors_count"] * 0.3 +
    df["issues"] * 0.3
)
df["success_score"] = (
    df["stars"] * 0.5 +
    df["forks"] * 0.3 +
    df["contributors_count"] * 0.2
)
df["engagement_ratio"] = df["forks"] / df["stars"].replace(0,1)
df["contribution_efficiency"] = df["total_contributions"] / df["contributors_count"].replace(0,1)

#### Repo Analysis
# repository growth rate
top_growth = df.sort_values("stars_per_day", ascending=False)
print("Top Growing Repositories:")
print(top_growth[["name", "stars_per_day"]])

# language analysis
df["language"] = df["language"].fillna("Unknown")
lang = df.groupby("language")["stars"].mean().sort_values(ascending=False)
print("Average Stars per Language:")
print(lang)

# commit frequency
print("\nCommit Frequency Leaders:")
print(df.sort_values("commit_frequency", ascending=False)[["name", "commit_frequency"]])

# most successful repositories
print("\nTop Successful Repositories:")
print(df.sort_values("success_score", ascending=False)[["name", "success_score"]])

# strongest communities
print("\nStrongest Communities:")
print(df.sort_values("contributors_count", ascending=False)[["name", "contributors_count"]])

