import os
import sys
import getopt
import requests
import json
import subprocess

from src.utils import *
from src.utils import _prettify, _display_json, _display_as_tree
from src.commits import get_last_commit

"""
example in curl:
curl -L \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer <YOUR-TOKEN>" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/OWNER/REPO/contents/PATH
"""


# Get repository contents

def get_repository_contents(owner, repo, format="json", path=""):
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
    print(response.json())
    #_prettify(response.json()[0])
    _display_as_tree(response.json())
    return response.json()[0]



def list_repository_contents(owner, repo, format="json", recursive=False, path=""):
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
    #data = get_repo_contents(owner, repo, format, path)
    data = get_repository_tree(owner, repo, recursive=recursive)

    return data

# get repo releases
def get_repository_releases(owner, repo, format="json"):
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

# get file contents
def get_file_content(owner, repo, file):
    """
    Retrieves the contents of a file in a given repository.

    Parameters:
    owner (str): The owner of the repository.
    repo (str): The name of the repository.
    file (str): The path to the file.

    Returns:
    None
    """
    accept = "application/vnd.github+json"
    url = os.environ["API_URL"] + "/repos/" + owner + "/" + repo + "/contents/" + file
    authorization = "Bearer " + os.environ["TOKEN"]
    version = os.environ["API_VERSION"]

    response = requests.get(url, headers={"Accept": accept, "Authorization": authorization, "X-GitHub-Api-Version": version})

    # create data
    response = response.json()

    data = {}
    data["name"] = response["name"]
    data["path"] = response["path"]
    data["content"] = response["content"]
    data["encoding"] = response["encoding"]

    return data

# seaarch for file in repo
def search_repository_file(owner, repo, file):
    """
    Retrieves the contents of a file in a given repository.

    Parameters:
    owner (str): The owner of the repository.
    repo (str): The name of the repository.
    file (str): The path to the file.

    Returns:
    None
    """
    accept = "application/vnd.github+json"
    url = os.environ["API_URL"] + "/search/code?q=" + file + "+in:file+repo:" + owner + "/" + repo
    authorization = "Bearer " + os.environ["TOKEN"]
    version = os.environ["API_VERSION"]

    response = requests.get(url, headers={"Accept": accept, "Authorization": authorization, "X-GitHub-Api-Version": version})

    # create data
    response = response.json()

    data = {}
    data["total_count"] = response["total_count"]
    data["incomplete_results"] = response["incomplete_results"]
    data["items"] = response["items"]

    return data

# get repo file tree
def get_repository_tree(owner, repo, sha='', recursive="false"):
    """
    Retrieves the contents of a file in a given repository.

    Parameters:
    owner (str): The owner of the repository.
    repo (str): The name of the repository.
    sha (str): The sha of the tree.

    Returns:
    None
    """

    # use default sha if none is provided, with the last commit
    if sha == '':
        sha = get_last_commit(owner, repo)
    

    accept = "application/vnd.github+json"
    url = os.environ["API_URL"] + "/repos/" + owner + "/" + repo + "/git/trees/" + sha
    
    authorization = "Bearer " + os.environ["TOKEN"]
    version = os.environ["API_VERSION"]

    params = {"recursive": recursive}

    response = requests.get(url, headers={"Accept": accept, "Authorization": authorization, "X-GitHub-Api-Version": version}, params=params)

    # create data
    response = response.json()['tree']

    _display_as_tree(response)

    return

# get repositories of a given owner
def _get_owner_repositories(owner):
    """
    Retrieves the repositories of a given user

    Parameters:
    owner (str): The owner of the repository.

    Returns:
    None
    """
    accept = "application/vnd.github+json"
    url = os.environ["API_URL"] + "/orgs/" + owner + "/repos"
    print(url)
    authorization = "Bearer " + os.environ["TOKEN"]
    version = os.environ["API_VERSION"]

    response = requests.get(url, headers={"Accept": accept, "Authorization": authorization, "X-GitHub-Api-Version": version})

    # create data
    response = response.json()

    repos = [repo['name'] for repo in response]

    return repos
