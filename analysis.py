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


# repository stability
df["stability_score"] = df["stars"] / df["issues"].replace(0,1)
print("\nMost Stable Repositories:")
print(df.sort_values("stability_score", ascending=False)[["name", "stability_score"]])



# Most Dominant Contributor Per Repo
def top_contributor(contributors):
    if not contributors:
        return None
    top = max(contributors, key=lambda x: x.get("contributions", 0))
    return top.get("login")
df["top_contributor"] = df["contributors"].apply(top_contributor)
print("\nTop Contributor per Repository:")
print(df[["name", "top_contributor"]])

#Commits per user
from collections import Counter
def commits_per_user(commits):
    users = [c["author"] for c in commits if c["author"]]
    return Counter(users)

#Growth over time
import pandas as pd
def commits_growth(commits):
    df = pd.DataFrame(commits)
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M")

    return df.groupby("month").size()

#Active contributors
def active_contributors(commits):
    return len(set(c["author"] for c in commits if c["author"]))