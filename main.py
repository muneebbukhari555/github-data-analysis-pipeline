import requests
import pandas as pd
import os
from datetime import datetime
from db import insert_data

TOKEN = os.getenv("GITHUB_TOKEN")
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
    
def fetch_contributors(repo, max_pages=3):
    contributors = []
    page = 1
    while page <= max_pages:
        url = f"https://api.github.com/repos/{repo}/contributors?per_page=100&page={page}"
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            break
        data = response.json()
        if not data or isinstance(data, dict):
            break
        contributors.extend(data)
        if len(data) < 100:
            break
        page += 1
    return contributors

def fetch_commits(repo, max_pages=5):  # LIMIT added
    commits = []
    page = 1
    while page <= max_pages:
        url = f"https://api.github.com/repos/{repo}/commits?per_page=100&page={page}"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 403:
                print("Rate limit hit. Sleeping...")
                time.sleep(60)
                continue
            data = response.json()
            if not data or isinstance(data, dict):
                break
            commits.extend(data)
            if len(data) < 100:
                break
            page += 1
        except requests.exceptions.RequestException as e:
            print("Request failed:", e)
            break
    return commits

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