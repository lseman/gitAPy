import os
import sys
import getopt
import requests
import json

"""
example in curl:
curl -L \
  -X PUT \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer <YOUR-TOKEN>" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/OWNER/REPO/contents/PATH \
  -d '{"message":"my commit message","committer":{"name":"Monalisa Octocat","email":"octocat@github.com"},"content":"bXkgbmV3IGZpbGUgY29udGVudHM="}'
"""

def put_repo_contents(owner, repo, path, message, content, format="json", sha=None):
    """
    Uploads or updates a file in a GitHub repository.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
        path (str): The path of the file in the repository.
        message (str): The commit message.
        content (str): The content of the file.
        format (str, optional): The format of the content. Defaults to "json".
        sha (str, optional): The SHA of the file if it already exists. Defaults to None.

    Returns:
        dict: The JSON response from the API.

    """
    if format == "json":
        accept = "application/vnd.github+json"
    url = API_URL + "/repos/" + owner + "/" + repo + "/contents/" + path
    authorization = "Bearer " + TOKEN
    version = API_VERSION
    data = {"message": message, "committer": {"name": "Laio O. Seman", "email": "laio@ieee.org"}, "content": content}

    # if sha=None, then it's a new file
    # if sha != None, then it's an update
    if sha != None:
        data["sha"] = sha

    response = request.put(url, headers={"Accept": accept, "Authorization": authorization, "X-GitHub-Api-Version": version}, data=data)

    return get_json(response)



"""
curl -L \
  -X DELETE \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer <YOUR-TOKEN>" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/OWNER/REPO/contents/PATH \
  -d '{"message":"my commit message","committer":{"name":"Monalisa Octocat","email":"octocat@github.com"},"sha":"329688480d39049927147c162b9d2deaf885005f"}'
"""

def del_repo_contents(owner, repo, path, message, sha, format="json"):
    """
    Deletes the contents of a repository at the specified path.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
        path (str): The path to the contents to be deleted.
        message (str): The commit message.
        sha (str): The SHA of the commit.
        format (str, optional): The format of the response. Defaults to "json".

    Returns:
        dict: The JSON response from the API.
    """
    if format == "json":
        accept = "application/vnd.github+json"
    url = API_URL + "/repos/" + owner + "/" + repo + "/contents/" + path
    authorization = "Bearer " + TOKEN
    version = API_VERSION
    data = {"message": message, "committer": {"name": "Laio O. Seman", "email": "laio@iee.org", "sha": sha}}

    response = request.delete(url, headers={"Accept": accept, "Authorization": authorization, "X-GitHub-Api-Version": version}, data=data)

    return get_json(response)