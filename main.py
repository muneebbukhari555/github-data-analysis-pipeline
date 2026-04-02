import requests
import pandas as pd
import matplotlib.pyplot as plt
import os

TOKEN = os.getenv("GIT_TOKEN")
headers = {
    "Authorization": f"Bearer {TOKEN}"
}
repos = [
    "kubernetes/kubernetes",
    "pytorch/pytorch",
    "ansible/ansible",
    "scikit-learn/scikit-learn",
    "tensorflow/tensorflow",
    "apache/spark",
    "docker/compose",
    "prometheus/prometheus"
]

dataset = []

def fetch_repo_data(repo):
    url = f"https://api.github.com/repos/{repo}"
    response = requests.get(url, headers=headers)
    return response.json()
    
def fetch_contributors(repo):
    url = f"https://api.github.com/repos/{repo}/contributors"
    response = requests.get(url, headers=headers)
    return len(response.json())

def fetch_commits(repo):
    url = f"https://api.github.com/repos/{repo}/commits"
    response = requests.get(url, headers=headers)
    return len(response.json())

def process_repo(repo):
    data = fetch_repo_data(repo)

    return {
        "name": repo,
        "stars": data.get("stargazers_count", 0),
        "forks": data.get("forks_count", 0),
        "issues": data.get("open_issues_count", 0),
        "language": data.get("language"),
        "created_at": data.get("created_at"),
        "updated_at": data.get("updated_at"),
        "contributors": fetch_contributors(repo),
        "recent_commits": fetch_commits(repo)
    }

#### Data Processing 
for repo in repos:
    try:
        dataset.append(process_repo(repo))
    except:
        print(f"Error processing {repo}")

df = pd.DataFrame(dataset)
df.head()
df.to_csv("github_data.csv", index=False)
print(df.head())

df["created_at"] = pd.to_datetime(df["created_at"], utc=True)
df["updated_at"] = pd.to_datetime(df["updated_at"], utc=True)
# Use UTC time
df["age_days"] = (pd.Timestamp.now(tz="UTC") - df["created_at"]).dt.days
# Handle missing language
df["language"] = df["language"].fillna("Unknown")

print(df.describe())
print(df["language"].value_counts())

df["stars_per_day"] = df["stars"] / df["age_days"]
df["forks_per_star"] = df["forks"] / df["stars"]
df["contributors_per_star"] = df["contributors"] / df["stars"]

df.sort_values("stars", ascending=False)[["name", "stars"]]

### Scenario:1 Popularity Visualization
df["stars"].plot(kind="bar", title="Stars per Repository")
plt.show()

# Scatter plot
plt.scatter(df["forks"], df["stars"])
plt.xlabel("Forks")
plt.ylabel("Stars")
plt.title("Forks vs Stars")
plt.show()