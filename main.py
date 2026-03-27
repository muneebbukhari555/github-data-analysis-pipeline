import requests

TOKEN = "ghp_xxxxxxxxxxxxxx"
headers = {
    "Authorization": f"Bearer {TOKEN}"
}

# List of repositories
repos = [
    "kubernetes/kubernetes"
]
url = f"https://api.github.com/repos/kubernetes/kubernetes"
response = requests.get(url, headers=headers)

print(response.json())