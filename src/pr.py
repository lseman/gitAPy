import os
import sys
import getopt
import requests
import json
import subprocess

from src.utils import _prettify, _display_json

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

    #print(response)
    data = {}
    for item in response:
        data[item["title"]] = [item["number"], item["user"]["login"], item["created_at"], item["updated_at"], item["state"]]

    _prettify(data)

# create pull request
def create_pull_request(owner, repo, title, head, base, body="", format="json"):
    """
    Creates a pull request for a given repository.

    Parameters:
    owner (str): The owner of the repository.
    repo (str): The name of the repository.
    title (str): The title of the pull request.
    head (str): The name of the branch where your changes are implemented.
    base (str): The name of the branch you want your changes pulled into.
    body (str, optional): The contents of the pull request. Defaults to "".
    format (str, optional): The format of the response. Defaults to "json".

    Returns:
    None
    """
    if format == "json":
        accept = "application/vnd.github+json"
    url = os.environ["API_URL"] + "/repos/" + owner + "/" + repo + "/pulls"
    print(url)
    authorization = "Bearer " + os.environ["TOKEN"]
    version = os.environ["API_VERSION"]

    params = {"title": title, "head": head, "base": base, "body": body}
    print(params)

    response = requests.post(url, headers={"Accept": accept, "Authorization": authorization, "X-GitHub-Api-Version": version}, json=params)

    # create data
    response = response.json()

    return response["number"]


# merge pull request
def merge_pull_request(owner, repo, pull_number, commit_message="", format="json"):
    """
    Merges a pull request for a given repository.

    Parameters:
    owner (str): The owner of the repository.
    repo (str): The name of the repository.
    pull_number (int): The number of the pull request.
    commit_message (str, optional): The commit message to use for the merge commit. Defaults to "".
    format (str, optional): The format of the response. Defaults to "json".

    Returns:
    None
    """
    if format == "json":
        accept = "application/vnd.github+json"
    url = os.environ["API_URL"] + "/repos/" + owner + "/" + repo + "/pulls/" + str(pull_number) + "/merge"
    authorization = "Bearer " + os.environ["TOKEN"]
    version = os.environ["API_VERSION"]

    params = {"commit_message": commit_message}

    response = requests.put(url, headers={"Accept": accept, "Authorization": authorization, "X-GitHub-Api-Version": version}, json=params)

    # create data
    response = response.json()

    print(response)

    _prettify(data)

def _get_pull_request(owner, repo, pull_number, format="json"):
    """
    Retrieves a pull request for a given repository.

    Parameters:
    owner (str): The owner of the repository.
    repo (str): The name of the repository.
    pull_number (int): The number of the pull request.
    format (str, optional): The format of the response. Defaults to "json".

    Returns:
    None
    """
    if format == "json":
        accept = "application/vnd.github+json"
    url = os.environ["API_URL"] + "/repos/" + owner + "/" + repo + "/pulls/" + str(pull_number)
    authorization = "Bearer " + os.environ["TOKEN"]
    version = os.environ["API_VERSION"]

    response = requests.get(url, headers={"Accept": accept, "Authorization": authorization, "X-GitHub-Api-Version": version})

    # create data
    response = response.json()

    #print(response)

    _display_json(response)

# show pull request discussion
def get_pull_request(owner, repo, pull_number, options="issues/comments", format="json"):
    """
    Retrieves a pull request discussion for a given repository.

    Parameters:
    owner (str): The owner of the repository.
    repo (str): The name of the repository.
    pull_number (int): The number of the pull request.
    format (str, optional): The format of the response. Defaults to "json".

    Returns:
    None
    """

    options = options.split("/")
    if format == "json":
        accept = "application/vnd.github+json"
    url = os.environ["API_URL"] + "/repos/" + owner + "/" + repo + "/" + options[0] + "/" + str(pull_number) + "/" + options[1]
    authorization = "Bearer " + os.environ["TOKEN"]
    version = os.environ["API_VERSION"]

    response = requests.get(url, headers={"Accept": accept, "Authorization": authorization, "X-GitHub-Api-Version": version})

    # create data
    response = response.json()

    data = {}
    for item in response:
        data[item["id"]] = [item["user"]["login"], item["created_at"], item["updated_at"], item["body"]]

    _prettify(data)