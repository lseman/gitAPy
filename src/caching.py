import os
import sys
import getopt
import requests
import json
import subprocess

def _get_owner_list():
    """
    Get a list of all owners in the database.

    Returns:
        list: A list of all owners in the database.
    """
    # get com XDG_CONFIG_HOME/gitapy/cache/owners.txt
    if os.environ.get("XDG_CONFIG_HOME") != None:
        owner_list_path = os.environ["XDG_CONFIG_HOME"] + "/gitapy/cache/owners.txt"
    else:
        owner_list_path = os.environ["HOME"] + "/.config/gitapy/cache/owners.txt"

    with open(owner_list_path, "r") as f:
        owner_list = f.read().splitlines()

    return owner_list

def _update_owner_list(owner):
    """
    Get a list of all owners in the database.

    Returns:
        list: A list of all owners in the database.
    """
    # get com XDG_CONFIG_HOME/gitapy/cache/owners.txt
    if os.environ.get("XDG_CONFIG_HOME") != None:
        owner_list_path = os.environ["XDG_CONFIG_HOME"] + "/gitapy/cache/owners.txt"
    else:
        owner_list_path = os.environ["HOME"] + "/.config/gitapy/cache/owners.txt"

    with open(owner_list_path, "r") as f:
        owner_list = f.read().splitlines()

    # check if owner is in the list, if it is not, add it
    if owner not in owner_list:
        owner_list.append(owner)
        with open(owner_list_path, "w") as f:
            for owner in owner_list:
                f.write(owner + "\n")

    return