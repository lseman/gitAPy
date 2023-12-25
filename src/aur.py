
# Script to consume the AUR API
import requests
import json
import sys
import getopt
import subprocess
from rich.console import Console
import re
import os

"""
    name (search by package name only)
    name-desc (search by package name and description)
    maintainer (search by package maintainer)
    depends (search for packages that depend on keywords)
    makedepends (search for packages that makedepend on keywords)
    optdepends (search for packages that optdepend on keywords)
    checkdepends (search for packages that checkdepend on keywords)
"""

def check_package_aur(package):
    """
    Check if a package exists in the AUR.

    Args:
        package (str): The name of the package to check for.

    Returns:
        bool: True if the package exists, False otherwise.
    """
    
    AUR_API = "https://aur.archlinux.org/rpc/v5/"
    # get list of packages, sort by popularity, return 10
    url = AUR_API + "search/" + package

    # limit number of results
    query = {"limit": 10}

    print(url)
    response = requests.get(url, params=query)
    data = response.json()

    print(data)

def get_package_info(package):
    """
    Get information about a package from the AUR.

    Args:
        package (str): The name of the package to get information about.

    Returns:
        dict: A dictionary containing information about the package.
    """
    AUR_API = "https://aur.archlinux.org/rpc/v5/"

    url = AUR_API + "info/" + package

    response = requests.get(url)
    data = response.json()

    print(data)