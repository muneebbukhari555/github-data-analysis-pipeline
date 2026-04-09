import requests
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime
from db import insert_data

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
    url = f"https://api.github.com/repos/{repo}/contributors?per_page=100"
    response = requests.get(url, headers=headers)
    return len(response.json())

def fetch_commits(repo):
    url = f"https://api.github.com/repos/{repo}/commits?per_page=100"
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

for record in dataset:
    record["timestamp"] = datetime.utcnow()   

df = pd.DataFrame(dataset)
df.to_csv("github_data.csv", index=False)

insert_data(dataset)
print("Data stored in MongoDB")

print(df.head())