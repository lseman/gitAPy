import os
import sys
import getopt
import requests
import json
import subprocess

from src.pr import *


def merge_fork_upstream(owner, repo, branch="master"):
    """
    Updates a fork to match the upstream repository.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.

    Returns:
        None
    """
    pr_number = create_pull_request(owner, repo, "Update " + repo, owner + ":" + branch, "upstream:" + branch, "Update " + repo)
    merge_pull_request(owner, repo, pr_number, "Update " + repo)

# get upstream ref
def get_upstream_ref(owner, repo, branch="master"):
    """
    Retrieves the SHA of the upstream repository.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.

    Returns:
        None
    """
    accept = "application/vnd.github+json"
    url = os.environ["API_URL"] + "/repos/" + owner + "/" + repo + "/git/refs/heads/" + branch
    authorization = "Bearer " + os.environ["TOKEN"]
    version = os.environ["API_VERSION"]

    response = requests.get(url, headers={"Accept": accept, "Authorization": authorization, "X-GitHub-Api-Version": version})

    # create data
    response = response.json()

    data = {}
    data["sha"] = response["object"]["sha"]

    print(data)

    return data