# Script to consume the GitHub API
import requests
import json
import sys
import getopt
import subprocess
import os
from datetime import datetime, timedelta

from src.commits import *
from src.pr import *
from src.organization import *

def cachy():
    owner = "CachyOS"

    data = list_repos_organization(owner)

    # get repo names from data
    lista = ""
    for item in data:
        lista += item["name"] + "\n"

    # give gum option with subprocess to select a repo
    repo = subprocess.run(["gum", "filter"], input=lista, text=True, stdout=subprocess.PIPE)
    repo = repo.stdout.strip()

    option = subprocess.run(["gum", "choose"], input="commits\npulls", text=True, stdout=subprocess.PIPE)
    option = option.stdout.strip()

    if option == "pulls":
        list_pull_requests(owner, repo)
    else:
        list_commits(owner, repo)