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
from src.reading import *
import base64
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

def cachy_update():
    owner = "CachyOS"

    # get all PKGBUILD files in CachyOS-PKGBUILDs

    data = get_repo_tree(owner, "CachyOS-PKGBUILDs", "master", recursive="true")
    tree = data["tree"]
    PKGBUILDS = []
    for item in tree:
        if item["type"] == "blob":
            # get all PKGBUILD files in the directory
            path = item["path"]
            if path.endswith("PKGBUILD"):
                PKGBUILDS.append(path)
    
    # filter PKGBUILDs that do start with cachyos
    #PKGBUILDS = [x for x in PKGBUILDS if x.startswith("cachyos")]
    PKGBUILDS = [x for x in PKGBUILDS if not x.startswith("cachyos-")]


    # get all PKGBUILD files in CachyOS-PKGBUILDs
    for pkg in PKGBUILDS:
        data = get_file_content(owner, "CachyOS-PKGBUILDs", file=pkg)
        content = base64.b64decode(data["content"]).decode("utf-8")
        # extract pkgname, pkgver, pkgrel and url from content
        try:
            pkgbase = content.split("pkgbase=")[1].split("\n")[0]
        except:
            pkgbase = ''
        pkgname = content.split("pkgname=")[1].split("\n")[0]
        pkgver = content.split("pkgver=")[1].split("\n")[0]
        pkgrel = content.split("pkgrel=")[1].split("\n")[0]
        try:
            url = content.split("url=")[1].split("\n")[0]
        except:
            url = ''

        print(pkgname, pkgver, pkgrel, url)
    