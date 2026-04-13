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

# top contributors accross all repos
all_users = []
for repo in df["contributors"]:
    for c in repo:
        all_users.append(c.get("login"))
top_users = Counter(all_users).most_common(10)
print("\nTop Contributors Across Repositories:")
print(top_users)

# repository stability
df["stability_score"] = df["stars"] / df["issues"].replace(0,1)
print("\nMost Stable Repositories:")
print(df.sort_values("stability_score", ascending=False)[["name", "stability_score"]])

###############################################
#extract commit authors
from collections import Counter
all_commit_users = []
for commits in df["recent_commits"]:
    for c in commits:
        try:
            user = c["author"]["login"]
            if user:
                all_commit_users.append(user)
        except:
            continue
top_committers = Counter(all_commit_users).most_common(10)
print("\nTop Committers Across Repositories:")
print(top_committers)

#Use commit author metadata
def extract_commit_authors(commits):
    users = []
    for c in commits:
        try:
            users.append(c["commit"]["author"]["name"])
        except:
            continue
    return users
df["commit_authors"] = df["recent_commits"].apply(extract_commit_authors)
all_users = []
for users in df["commit_authors"]:
    all_users.extend(users)
print(Counter(all_users).most_common(10))

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