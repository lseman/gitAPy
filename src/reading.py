import os
import sys
import getopt
import requests
import json
import subprocess

from src.utils import get_json

"""
example in curl:
curl -L \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer <YOUR-TOKEN>" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/OWNER/REPO/contents/PATH
"""


# Get repository contents
def get_repo_contents(owner, repo, format="json", path=""):
    """
    Retrieves the contents of a repository.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
        format (str, optional): The format of the response. Defaults to "json".
        path (str, optional): The path to the file or directory. Defaults to "".

    Returns:
        dict: The contents of the repository in the specified format.
    """
    if format == "json":
        accept = "application/vnd.github+json"
    url = os.environ["API_URL"] + "/repos/" + owner + "/" + repo + "/contents/" + path
    authorization = "Bearer " + os.environ["TOKEN"]
    version = os.environ["API_VERSION"]
    response = requests.get(
        url,
        headers={
            "Accept": accept,
            "Authorization": authorization,
            "X-GitHub-Api-Version": version,
        },
    )
    return get_json(response)


# def full repository contents
def full_repo_contents(owner, repo, format="json", path="", items={}, dirname=""):
    """
    Recursively retrieves the full contents of a repository, including directories and files.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
        format (str, optional): The format of the response. Defaults to "json".
        path (str, optional): The path within the repository to start retrieving contents from. Defaults to "".
        items (dict, optional): A dictionary to store the retrieved contents. Defaults to {}.
        dirname (str, optional): The directory name. Defaults to ''.

    Returns:
        dict: A dictionary containing the full contents of the repository.
    """
    data = get_repo_contents(owner, repo, format, path)

    if dirname != "":
        dirname = dirname + "/"
    items[dirname] = []
    for item in data:
        if item["type"] == "dir":
            full_repo_contents(
                owner, repo, format, item["path"], items, dirname + item["name"]
            )
        else:
            items[dirname].append(item["name"])

    return items


def list_repo_contents(owner, repo, format="json", recursive=True, path=""):
    """
    List the contents of a repository.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
        format (str, optional): The format of the output. Defaults to "json".
        recursive (bool, optional): Whether to list contents recursively. Defaults to True.
        path (str, optional): The path within the repository to list contents from. Defaults to "".

    Returns:
        None
    """
    if recursive == False:
        data = get_repo_contents(owner, repo, format, path)
    else:
        data = full_repo_contents(owner, repo, format, path)

    subprocess.run(["jq"], input=json.dumps(data).encode("utf-8"))

    return

# get repo releases
def get_repo_releases(owner, repo, format="json"):
    """
    Retrieves a list of releases for a given repository.

    Parameters:
    owner (str): The owner of the repository.
    repo (str): The name of the repository.
    format (str, optional): The format of the response. Defaults to "json".

    Returns:
    None
    """
    if format == "json":
        accept = "application/vnd.github+json"
    url = os.environ["API_URL"] + "/repos/" + owner + "/" + repo + "/releases"
    authorization = "Bearer " + os.environ["TOKEN"]
    version = os.environ["API_VERSION"]

    response = requests.get(url, headers={"Accept": accept, "Authorization": authorization, "X-GitHub-Api-Version": version})

    # create data
    response = response.json()

    data = {}
    for item in response:
        data[item["name"]] = [item["tag_name"], item["published_at"], item["body"]]

    subprocess.run(["jq"], input=json.dumps(data), text=True)

    return