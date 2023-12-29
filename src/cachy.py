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
from src.aur import *
from src.db import *
from src.utils import *
from src.aur import *
from src.issues import *
# import console from rich
from rich.console import Console

import base64

''''
           $3.$1-------------------------:
          .$2+=$1========================.
         :$2++$1===$2++===$1===============-       :$2++$1-
        :$2*++$1====$2+++++==$1===========-        .==:
       -$2*+++$1=====$2+***++=$1=========:
      =$2*++++=$1=======------------:
     =$2*+++++=$1====-                     $3...$1
   .$2+*+++++$1=-===:                    .$2=+++=$1:
  :$2++++$1=====-==:                     -***$2**$1+
 :$2++=$1=======-=.                      .=+**+$3.$1
.$2+$1==========-.                          $3.$1
 :$2+++++++$1====-                                $3.$1--==-$3.$1
  :$2++$1==========.                             $3:$2+++++++$1$3:
   $1.-===========.                            =*****+*+
    $1.-===========:                           .+*****+:
      $1-=======$2++++$1:::::::::::::::::::::::::-:  $3.$1---:
       :======$2++++$1====$2+++******************=.
        $1:=====$2+++$1==========$2++++++++++++++*-
         $1.====$2++$1==============$2++++++++++*-
          $1.===$2+$1==================$2+++++++:
           $1.-=======================$2+++:
             $3..........................
'''

def print_logo():
    print("""
           \x1b[32m.\x1b[92m-------------------------:
          .\x1b[92m+=\x1b[92m========================.
         :\x1b[92m++\x1b[92m===\x1b[92m++===\x1b[92m===============-       :\x1b[92m++\x1b[92m-
        :\x1b[92m*++\x1b[92m====\x1b[92m+++++==\x1b[92m===========-        .==:
       -\x1b[92m*+++\x1b[92m=====\x1b[92m+***++=\x1b[92m=========:
      =\x1b[92m*++++=\x1b[92m=======------------:
     =\x1b[92m*+++++=\x1b[92m====-                     \x1b[32m...\x1b[92m
   .\x1b[92m+*+++++\x1b[92m=-===:                    .\x1b[92m=+++=\x1b[92m:
  :\x1b[92m++++\x1b[92m=====-==:                     -***\x1b[92m**\x1b[92m+
 :\x1b[92m++=\x1b[92m=======-=.                      .=+**+\x1b[32m.\x1b[92m
.\x1b[92m+\x1b[92m==========-.                          \x1b[32m.\x1b[92m
 :\x1b[92m+++++++\x1b[92m====-                                \x1b[32m.\x1b[92m--==-\x1b[32m.\x1b[92m
  :\x1b[92m++\x1b[92m==========.                             \x1b[32m:\x1b[92m+++++++\x1b[92m\x1b[32m:
   \x1b[92m.-===========.                            =*****+*+
    \x1b[92m.-===========:                           .+*****+:
      \x1b[92m-=======\x1b[92m++++\x1b[92m:::::::::::::::::::::::::-:  \x1b[32m.\x1b[92m---:
       :======\x1b[92m++++\x1b[92m====\x1b[92m+++******************=.
        \x1b[92m:=====\x1b[92m+++\x1b[92m==========\x1b[92m++++++++++++++*-
         \x1b[92m.====\x1b[92m++\x1b[92m==============\x1b[92m++++++++++*-
          \x1b[92m.===\x1b[92m+\x1b[92m==================\x1b[92m+++++++:
           \x1b[92m.-=======================\x1b[92m+++:
             \x1b[32m..........................
\x1b[0m""")

def cachy():
    # print CachyOS logo in ascii art
    print_logo()


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

###################################################
def extract_package_data(content):
    """
    Extracts package data from the given content.

    Args:
        content (str): The content to extract package data from.

    Returns:
        dict: A dictionary containing the extracted package data.
              The dictionary has the following keys:
              - 'pkgbase': The base package name.
              - 'pkgname': The package name.
              - 'pkgver': The package version.
              - 'pkgrel': The package release.
              - 'url': The package URL.
    """
    lines = content.split("\n")
    data = {}
    for line in lines:
        if line.startswith("pkgbase="):
            data["pkgbase"] = line.split("=")[1]
        elif line.startswith("pkgname="):
            data["pkgname"] = line.split("=")[1]
        elif line.startswith("pkgver="):
            data["pkgver"] = line.split("=")[1]
        elif line.startswith("pkgrel="):
            data["pkgrel"] = line.split("=")[1]
        elif line.startswith("url="):
            data["url"] = line.split("=")[1]
    return data

def get_package_versions(key, value, owner):
    data = get_file_content(owner, "CachyOS-PKGBUILDs", file=value)
    content = base64.b64decode(data["content"]).decode("utf-8")
    package_data = extract_package_data(content)
    return key, package_data

def print_pacman_separator_colored():
    """
    Prints a separator line with colored elements representing Pac-Man, dots, and a ghost.
    """

    # ANSI color codes
    yellow = "\033[93m"  # Yellow for Pac-Man
    white = "\033[97m"  # White for dots
    blue = "\033[94m"  # Blue for the ghost
    reset = "\033[0m"  # Reset color

    # Elements with colors
    pacman = yellow + "C" + reset
    dots = white + "." * 50 + reset
    ghost = blue + "[venepogodin]" + reset

    separator_line = pacman + dots + ghost
    print(separator_line)



def cachy_update():
    """
    Update the CachyOS packages by checking their versions against Arch Linux official repositories and AUR.

    This function performs the following steps:
    1. Retrieves all PKGBUILD files in the CachyOS-PKGBUILDs repository.
    2. Downloads the repository tarball.
    3. Finds the directory starting with "CachyOS-PKGBUILDS".
    4. Reads each PKGBUILD file, extracts package data, and stores it in a dictionary.
    5. Checks the versions of each package against Arch Linux official repositories.
    6. If the package is not found in Arch Linux, checks the version against AUR.

    Note: This function assumes the presence of the following helper functions:
    - print_logo(): Prints the CachyOS logo.
    - print_pacman_separator_colored(): Prints a separator line resembling a pacman eating dots or Rasputin.
    - create_archlinux_repo_list(): Creates a list of packages from Arch Linux official repositories.
    - get_package_info(pkgname): Retrieves package information from AUR.

    """
    owner = "CachyOS"
    print_logo()
    console = Console()
    get_repository_tarball(owner, "CachyOS-PKGBUILDs", "master", "zip")

    for root, dirs, files in os.walk("."):
        for name in dirs:
            if "CachyOS-PKGBUILDS" in name:
                folder = name
                break

    keys = {}
    for root, dirs, files in os.walk(folder):
        for name in files:
            if name == "PKGBUILD":
                if "cachy" not in name:
                    # read file and extract package data
                    with open(os.path.join(root, name), "r") as f:
                        content = f.read()
                    package_data = extract_package_data(content)
                    keys[package_data["pkgname"]] = package_data
    
    tree = create_archlinux_repo_list()
    # retrieve PKGBUILD info
    def check_versions(key, value):
        # if cachy is in the name, skip
        if "cachy" in key:
            return

        # check if pkgbase is empty
        if "pkgbase" not in value:
            pkgname = value["pkgname"]
        else:
            pkgname = value["pkgbase"]

        # print separator line like a pacman eating dots or rasputin
        print_pacman_separator_colored()
        console.print('Checking package', pkgname, style="bold green")

        pkgver, pkgrel = value["pkgver"], value["pkgrel"]
                 
        console.print('Checking version against Arch Linux official repositories', style="blue")
        console.print('Package name:', pkgname, style="bold")
        console.print('CachyOS:', pkgver, pkgrel)
        
        # check if key is a key in tree_version
        if key in tree:
            tree_version = tree[key]
            console.print('ArchLinux', tree_version['pkgver'], tree_version['pkgrel'])

            # check if version is different
            if str(tree_version['pkgver']) != pkgver:
                console.print('WARNING: Version is different', style="bold red")
                # if version is different, open an issue
                create_issue('lseman', "CachyOS-PKGBUILDs", pkgname + ": version is different", "Version is different for " + pkgname + ".\n\nCachyOS: " + pkgver + "-" + pkgrel + "\nArchLinux: " + tree_version['pkgver'] + "-" + tree_version['pkgrel'] + "\n\nPlease update the package. \n\n Bip bop, I'm a bot.")
                # create_issue(owner, "CachyOS-PKGBUILDs", "Version is different", "Version is different for " + pkgname + ".\n\nCachyOS: " + pkgver + "-" + pkgrel + "\nArchLinux: " + tree_version['pkgver'] + "-" + tree_version['pkgrel'] + "\n\nPlease update the package.", "bug")
            if str(tree_version['pkgrel']) != pkgrel:
                console.print('WARNING: Release is different', style="bold red")
        else:
            console.print('Package not found in ArchLinux', style="bold yellow")
            console.print('Checking version against AUR', style="blue")
            aur_version = get_package_info(key)
            if aur_version != 'NotFound':
                versioning = aur_version['Version'].split('-')
                aur_pkgver = versioning[0]
                aur_pkgrel = versioning[1]

                console.print('AUR', aur_pkgver, aur_pkgrel)

                # check if version is different
                if str(aur_pkgver) != pkgver:
                    console.print('WARNING: Version is different', style="bold red")
                    create_issue('lseman', "CachyOS-PKGBUILDs", pkgname + ": version is different", "Version is different for " + pkgname + ".\n\nCachyOS: " + pkgver + "-" + pkgrel + "\nArchLinux: " + tree_version['pkgver'] + "-" + tree_version['pkgrel'] + "\n\nPlease update the package. \n\n Bip bop, I'm a bot.")

                if str(aur_pkgrel) != pkgrel:
                    console.print('WARNING: Release is different', style="bold red")
            else:
                console.print('Does this package even exist?', style="bold white")

    for key, value in keys.items():
        check_versions(key, value)