# Script to consume the GitHub API
import requests
import json
import sys
import getopt
import subprocess
from rich.console import Console
import re
import os

"""
curl -L \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer <YOUR-TOKEN>" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/OWNER/REPO/tarball/REF
"""

# Get repository tarball

def get_repository_tarball(owner, repo, ref, format="zip"):
    """
    Get the tarball or zipball URL for a repository.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
        ref (str): The reference (branch, tag, or commit) to get the tarball or zipball for.
        format (str, optional): The format of the tarball or zipball. Defaults to "zip".

    Returns:
        str: The URL of the tarball or zipball.

    """
    if format == "zip":
        format = "zipball"
    elif format == "tar":
        format = "tarball"
    accept = "application/vnd.github+json"
    url = os.environ["API_URL"] + "/repos/" + owner + "/" + repo + "/" + format + "/" + ref
    authorization = "Bearer " + os.environ["TOKEN"]
    version = os.environ["API_VERSION"]
    response = requests.get(url, headers={"Accept": accept, "Authorization": authorization, "X-GitHub-Api-Version": version})
    return get_json(response)

### geting traffic of a repo
def get_repository_clones(owner, repo, format="json"):
    if format == "json":
        accept = "application/vnd.github+json"
    url = os.environ["API_URL"] + "/repos/" + owner + "/" + repo + "/traffic/views"
    print(url)
    authorization = "Bearer " + os.environ["TOKEN"]
    version = os.environ["API_VERSION"]
    
    query = {"per": "week"}

    response = requests.get(url, headers={"Accept": accept, "Authorization": authorization, "X-GitHub-Api-Version": version}, params=query)
    return get_json(response)


# define pretty print with subprocess and gum
def _pretty_print(data, format="json"):
    if format == "json":
        subprocess.run(["jq", "."], input=json.dumps(data).encode("utf-8"))


# Function to get the GitHub API response in JSON format
def _get_json(response):
    return response.json()
def _prettify(data):
    """
    Formats the given data using the jq command and prints the output with colors and formatting.

    Args:
        data (dict): The JSON data to be formatted.

    Returns:
        None
    """
    # Prepare the jq command
    jq_command = 'jq -r "to_entries|map(\\\"\(.key): \(.value|join(\\\", \\\"))\\\")|.[]"'

    # Run the jq command using a shell (be cautious of shell=True with dynamic inputs)
    jq_process = subprocess.Popen(jq_command, 
                                  shell=True, 
                                  stdin=subprocess.PIPE, 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE,
                                  text=True)

    # Pass JSON data to jq and get the output
    jq_output, _ = jq_process.communicate(json.dumps(data))
    # Create a Rich console
    console = Console()
    
    # Replace literal '\n' and '\r' with actual new lines
    formatted_output = jq_output.replace('\\n', '\n').replace('\\r', '')

    # Replace multiple newlines with a single newline
    formatted_output = re.sub(r'\n+', '\n', formatted_output)

    # Optional: Special formatting for lines starting with '*'
    formatted_lines = []
    for line in formatted_output.split('\n'):
        if line.strip().startswith('*'):
            # For example, make these lines blue
            formatted_lines.append("[green]" + line + "[/green]")
        else:
            formatted_lines.append(line)

    formatted_lines = "\n".join(formatted_lines)

    # remove last newline
    formatted_lines = formatted_lines[:-1]

    # Print the output with colors and formatting
    console.print(formatted_lines)

#  Function to search for the official git repo  of a given package, from the original developer
def search_git_package(package):
    """
    Search for a package in GitHub repositories.

    Args:
        package (str): The name of the package to search for.

    Returns:
        list: A list of full names of repositories that match the search query.
    """
    
    #  search if the package exists  in github
    url = os.environ["API_URL"] + "/search/repositories?q=" + package
    authorization = "Bearer " + os.environ["TOKEN"]
    version = os.environ["API_VERSION"]

    # sort by stars
    query = {}

    response = requests.get(url, headers={"Accept": "application/vnd.github.v3+json", "Authorization": authorization, "X-GitHub-Api-Version": version}, params=query)

    # create a list with the results
    data = response.json()
    items = data["items"]
    results = []
    for item in items:
        results.append(item["full_name"])

    print(results)


# Function to check if package exist in official arch repo, checking in the web
def check_archlinux_package(package):
    """
    Check if a package exists in the official Arch Linux repositories.

    Args:
        package (str): The name of the package to check for.

    Returns:
        bool: True if the package exists, False otherwise.
    """
    url = "https://archlinux.org/packages/search/json/?name=" + package
    response = requests.get(url)
    data = response.json()

    print(data)
    if data["valid"] == True:
        return True
    else:
        return False
