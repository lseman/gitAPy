# Script to consume the GitHub API
import requests
import json
import sys
import getopt
import subprocess
from rich.console import Console
import re
import os
from rich.tree import Tree
from rich import print as rprint
import urllib.request

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
    # download the file in the url, using curl or urllib
    urllib.request.urlretrieve(url, "repo.zip")
    # unzip the file
    subprocess.run(["unzip", "repo.zip"])
    # remove the zip file
    subprocess.run(["rm", "repo.zip"])

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

    return data

def get_archlinux_package(package):
    """
    Get information about a package from the official Arch Linux repositories.

    Args:
        package (str): The name of the package to get information about.

    Returns:
        dict: A dictionary containing information about the package.
    """
    repositores = ["core", "extra"]
    for repo in repositores:
        url = "https://archlinux.org/packages/" + repo + "/x86_64/" + package + "/json"
        response = requests.get(url)
        
        # check if response is not 404
        if response.status_code != 404:
            data = response.json()
            if data["pkgname"] == package:
                return data
    return 'NotFound'

# display json with jq
def _display_json(data):
    """
    Display the given data using the jq command.

    Args:
        data (dict): The JSON data to be displayed.

    Returns:
        None
    """
    subprocess.run(["jq", "."], input=json.dumps(data).encode("utf-8"))


class TreeNode:
    def __init__(self, name):
        self.name = name
        self.children = {}

    def insert(self, path_parts):
        if path_parts:
            first_part = path_parts[0]
            if first_part not in self.children:
                self.children[first_part] = TreeNode(first_part)
            self.children[first_part].insert(path_parts[1:])

def _build_tree(paths):
    root = TreeNode(None)  # Root node doesn't have a name
    for path in paths:
        parts = path.split('/')
        root.insert(parts)
    return root

def _build_rich_tree(node, level=0):
    # Define colors for different levels and leaf nodes
    colors = ["bold blue", "bold green", "magenta", "cyan", "yellow"]
    leaf_color = "bold red"

    # Determine the color based on the level and whether it's a leaf
    node_color = leaf_color if not node.children else colors[min(level, len(colors)-1)]

    # Create the tree node with the determined color
    if node.name is None:  # Root node
        tree = Tree("Git Repo", guide_style="bold bright_blue")
    else:
        tree = Tree(f"[{node_color}]{node.name}[/]")

    # Recursively build the tree for children
    for _, child_node in node.children.items():
        subtree = _build_rich_tree(child_node, level + 1)
        tree.add(subtree)
    return tree


# display json as tree, geting the name of the file and the hierarchy
def _display_as_tree(data):
    """
    Display the given data as a tree using the tree command.

    Args:
        data (dict): The JSON data to be displayed.

    Returns:
        None
    """
    paths = []
    names = []
    paths_only = []
    # first get the name of the file
    for item in data:
        #print('path: ' + item["path"])
        paths.append(item["path"])
        # extract the name as the last element of the path
        name = item["path"].split("/")[-1]
        #print('name: ' + name)
        names.append(name)
        paths_only.append(item["path"].split(name)[0])

    # now we have the name and the path
    # lets use this to pretty print with rich
    # Assuming 'data' is your list of items with paths
    paths = [item["path"] for item in data]
    tree_root = _build_tree(paths)
    rich_tree = _build_rich_tree(tree_root)  # Directly pass the root
    rprint(rich_tree)

# create archlinux repository list from
# http://archlinux.c3sl.ufpr.br/core/os/x86_64/
# http://archlinux.c3sl.ufpr.br/extra/os/x86_64/

def create_archlinux_repo_list():
    """
    Create a list of packages in the official Arch Linux repositories.

    Returns:
        list: A list of packages in the official Arch Linux repositories.
    """
    # create a list of packages
    packages = {}
    repositores = ["core", "extra"]
    for repo in repositores:
        download = "http://archlinux.c3sl.ufpr.br/" + repo + "/os/x86_64/" + repo + ".db.tar.gz"
        # download the file
        subprocess.run(["wget", download])
        # extract the file to a subdirectory
        subprocess.run(["mkdir", repo])
        subprocess.run(["tar", "-xf", repo + ".db.tar.gz", "-C", repo])
    for root, dirs, files in os.walk(repo):
        for name in files:
            if 'desc' in name:
                #print(os.path.join(root, name))
                with open(os.path.join(root, 'desc')) as f:
                    for line in f:
                        if line.startswith("%NAME%"):
                            # get the next line as the name
                            name = next(f)
                            packages[name.strip()] = {}
                        if line.startswith("%VERSION%"):
                            # get the next line as the version
                            version = next(f)
                            packages[name.strip()]["pkgver"] = version.split('-')[0].strip()
                            packages[name.strip()]["pkgrel"] = version.split('-')[1].strip()

    return packages