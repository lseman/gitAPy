import os
import sys
import getopt
import requests
import json
import subprocess

def create_issue(owner, repo, title, body, assignees=[], labels=[]):
    """
    Creates an issue in a given repository.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
        title (str): The title of the issue.
        body (str): The body of the issue.
        assignees (list): The list of assignees.
        labels (list): The list of labels.

    Returns:
        None
    """

    accept = "application/vnd.github+json"
    url = os.environ["API_URL"] + "/repos/" + owner + "/" + repo + "/issues"
    authorization = "Bearer " + os.environ["TOKEN"]
    version = os.environ["API_VERSION"]

    data = {}
    data["title"] = title
    data["body"] = body
    data["assignees"] = assignees
    data["labels"] = labels

    response = requests.post(url, headers={"Accept": accept, "Authorization": authorization, "X-GitHub-Api-Version": version}, data=json.dumps(data))

    # create data
    response = response.json()


    #print(response)

    return data

def list_issues(owner, repo):
    """
    Lists all issues in a given repository.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.

    Returns:
        None
    """

    accept = "application/vnd.github+json"
    url = os.environ["API_URL"] + "/repos/" + owner + "/" + repo + "/issues"
    authorization = "Bearer " + os.environ["TOKEN"]
    version = os.environ["API_VERSION"]

    response = requests.get(url, headers={"Accept": accept, "Authorization": authorization, "X-GitHub-Api-Version": version})

    # create data
    response = response.json()

    #print(response)

    return response
