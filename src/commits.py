# Script to consume the GitHub API
import requests
import json
import sys
import getopt
import subprocess
import os

"""
curl -L \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer <YOUR-TOKEN>" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/OWNER/REPO/commits
"""

def list_commits(owner, repo, format="json"):
    """
    Retrieves a list of commits for a given repository.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
        format (str, optional): The format of the response. Defaults to "json".

    Returns:
        dict: The JSON response from the API.

    """
    if format == "json":
        accept = "application/vnd.github+json"
    url = os.environ["API_URL"] + "/repos/" + owner + "/" + repo + "/commits"
    authorization = "Bearer " + os.environ["TOKEN"]
    version = os.environ["API_VERSION"]

    response = requests.get(url, headers={"Accept": accept, "Authorization": authorization, "X-GitHub-Api-Version": version})

    # create data
    response = response.json()

    data = {}
    for item in response:
        data[item["commit"]["author"]["name"]] = [item["commit"]["author"]["date"], item["commit"]["message"]]

    subprocess.run(["jq"], input=json.dumps(data), text=True)