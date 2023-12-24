import os
import sys
import getopt
import requests
import json
import subprocess

from src.utils import *

# list pull requests
def list_pull_requests(owner, repo, format="json"):
    """
    Retrieves a list of pull requests for a given repository.

    Parameters:
    owner (str): The owner of the repository.
    repo (str): The name of the repository.
    format (str, optional): The format of the response. Defaults to "json".

    Returns:
    None
    """
    if format == "json":
        accept = "application/vnd.github+json"
    url = os.environ["API_URL"] + "/repos/" + owner + "/" + repo + "/pulls"
    authorization = "Bearer " + os.environ["TOKEN"]
    version = os.environ["API_VERSION"]

    response = requests.get(url, headers={"Accept": accept, "Authorization": authorization, "X-GitHub-Api-Version": version})

    # create data
    response = response.json()

    data = {}
    for item in response:
        data[item["title"]] = [item["user"]["login"], item["created_at"], item["updated_at"], item["state"]]

    print(data)
    prettify(data)