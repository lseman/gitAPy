# Script to consume the GitHub API
import requests
import json
import sys
import getopt
import subprocess
import os
from datetime import datetime, timedelta

def list_repos_organization(org):
    """
    Retrieves a list of repositories for a given organization.

    Args:
        org (str): The name of the organization.

    Returns:
        dict: The JSON response from the API.

    """
    accept = "application/vnd.github+json"
    url = os.environ["API_URL"] + "/orgs/" + org + "/repos"
    authorization = "Bearer " + os.environ["TOKEN"]
    version = os.environ["API_VERSION"]

    response = requests.get(url, headers={"Accept": accept, "Authorization": authorization, "X-GitHub-Api-Version": version})

    # create data
    response = response.json()
    return(response)