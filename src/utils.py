# Script to consume the GitHub API
import requests
import json
import sys
import getopt
import subprocess
from rich import print
from rich.console import Console
import re

"""
curl -L \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer <YOUR-TOKEN>" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/OWNER/REPO/tarball/REF
"""

# Get repository tarball

def get_repo_tarball(owner, repo, ref, format="zip"):
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
    url = API_URL + "/repos/" + owner + "/" + repo + "/" + format + "/" + ref
    authorization = "Bearer " + TOKEN
    version = API_VERSION
    response = requests.get(url, headers={"Accept": accept, "Authorization": authorization, "X-GitHub-Api-Version": version})
    return get_json(response)

### geting traffic of a repo
def get_repo_clones(owner, repo, format="json"):
    if format == "json":
        accept = "application/vnd.github+json"
    url = API_URL + "/repos/" + owner + "/" + repo + "/traffic/views"
    print(url)
    authorization = "Bearer " + TOKEN
    version = API_VERSION
    
    query = {"per": "week"}

    response = requests.get(url, headers={"Accept": accept, "Authorization": authorization, "X-GitHub-Api-Version": version}, params=query)
    return get_json(response)




# define pretty print with subprocess and gum
def pretty_print(data, format="json"):
    if format == "json":
        subprocess.run(["jq", "."], input=json.dumps(data).encode("utf-8"))



# Function to get the GitHub API response in JSON format
def get_json(response):
    return response.json()

def prettify(data):
    """
    Formats the given data using the jq command and prints the output with colors and formatting.

    Args:
        data (dict): The JSON data to be formatted.

    Returns:
        None
    """
    # First, run the jq command
    jq_process = subprocess.Popen(
        ["jq", "-r", "to_entries|map(\"\(.key): \(.value|join(\", \"))\")|.[]"], 
        stdin=subprocess.PIPE, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        text=True
    )
    # Create a Rich console
    console = Console()

    # Pass JSON data to jq and get the output
    jq_output, _ = jq_process.communicate(json.dumps(data))

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

    # Join the lines back together
    final_output = '\n'.join(formatted_lines)

    # remove last newline
    final_output = final_output[:-1]

    # Print the output with colors and formatting
    console.print(final_output)