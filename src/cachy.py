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
from src.scrapper import *

import base64

"""'
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
"""


def print_logo():
    print(
        """
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
\x1b[0m"""
    )


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
    repo = subprocess.run(
        ["gum", "filter"], input=lista, text=True, stdout=subprocess.PIPE
    )
    repo = repo.stdout.strip()

    option = subprocess.run(
        ["gum", "choose"], input="commits\npulls", text=True, stdout=subprocess.PIPE
    )
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
    # populate data dictionary with all field from PKGBUILD, it means every line that:
    # is not a comment, is not empty, and contains an equal sign
    # we will stop when prepare() or build() is found
    for i, line in enumerate(lines):
        if line.startswith("#"):
            continue
        if line == "":
            continue
        if "=" not in line:
            continue
        if "prepare()" in line:
            break
        if "build()" in line:
            break
        # split line by equal sign
        key, value = line.split("=")[0], line.split("=")[1]
        # remove leading and trailing spaces
        key = key.strip()
        value = value.strip()
        # if key == "source" we need to keep populating this key with the next lines
        if key == "source":
            value = [value]
            if ")" not in value[0]:
                k = i + 1
                while True or k < len(lines):
                    # print(lines[k])
                    if ")" in lines[k]:
                        # print('break')
                        break
                    # get next line
                    # if line is empty, skip
                    try:
                        value.append(lines[k].strip())
                        k += 1
                    except IndexError:
                        break
                    # if line contains a closing parenthesis, stop

        if isinstance(value, list):
            for i, item in enumerate(value):
                value[i] = item.replace('"', "")
                value[i] = item.replace("'", "")
        else:
            value = value.replace('"', "")
            value = value.replace("'", "")
        # add to dictionary
        data[key] = value
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


def compare_versions(version1, version2):
    """
    Compare two version strings and return:
    -1 if version1 < version2
     0 if version1 == version2
     1 if version1 > version2
    """
    v1_tokens = [int(n) for n in version1.split('.')]
    v2_tokens = [int(n) for n in version2.split('.')]

    # Pad the shorter version with zeros
    max_length = max(len(v1_tokens), len(v2_tokens))
    v1_tokens.extend([0] * (max_length - len(v1_tokens)))
    v2_tokens.extend([0] * (max_length - len(v2_tokens)))

    for v1, v2 in zip(v1_tokens, v2_tokens):
        if v1 < v2:
            return -1
        elif v1 > v2:
            return 1
    return 0

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
                    # skip if pkgname ends with -git
                    if "-git" in package_data["pkgname"]:
                        continue
                    if "cachy" in package_data["pkgname"]:
                        continue
                    if "meta" in package_data["pkgname"]:
                        continue
                    if "nvidia" in package_data["pkgname"]:
                        continue
                    keys[package_data["pkgname"]] = package_data

    # create a web scrapper to visit the url and try to get the latest package version
    # teste = get_version_from_url('https://www.sqlite.org/')
    # print(teste)
    # print(pato)
    tree = create_archlinux_repo_list()

    # retrieve PKGBUILD info
    def check_versions(key, value):
        # if cachy is in the name, skip
        # if "cachy" in key:
        #    return

        # print separator line like a pacman eating dots or rasputin
        # print_pacman_separator_colored()
        # little treatment for pkgname without pkbase

        pkgname = value["pkgname"]
        key = pkgname
        # console.print('Checking package', pkgname, style="bold green")

        pkgver, pkgrel = value["pkgver"], value["pkgrel"]

        console.print(
            "DEBUG: Checking version against Arch Linux official repositories",
            style="white",
        )
        # console.print('Package name:', pkgname, style="bold")
        # console.print('CachyOS:', pkgver, pkgrel)

        # check if key is a key in tree_version
        if key in tree:
            tree_version = tree[key]
            console.print("ArchLinux", tree_version["pkgver"], tree_version["pkgrel"])

            # check if version is different
            if str(tree_version["pkgver"]) != pkgver:
                compare = compare_versions(tree_version["pkgver"], pkgver)
                if compare == -1:
                    console.print("DEBUG: Our version is newer.", style="bold blue")
                    return
                console.print("WARNING: Version is different", style="bold red")
                # if version is different, open an issue
                # create_issue(owner, "CachyOS-PKGBUILDs", pkgname + ": version is different", "Version is different for " + pkgname + ".\n\nCachyOS: " + pkgver + "-" + pkgrel + "\nArchLinux: " + tree_version['pkgver'] + "-" + tree_version['pkgrel'] + "\n\nPlease update the package. \n\n Bip bop, I'm a bot.")
            if str(tree_version["pkgrel"]) != pkgrel:
                console.print("WARNING: Release is different", style="bold red")
        else:
            console.print("DEBUG: Package not found in ArchLinux", style="white")
            console.print("DEBUG: Checking version against AUR", style="white")
            aur_version = get_package_info(key)
            if aur_version != "NotFound":
                versioning = aur_version["Version"].split("-")
                aur_pkgver = versioning[0]
                aur_pkgrel = versioning[1]

                aur_pkgver = aur_pkgver.split(":")[-1]
                console.print("AUR", aur_pkgver, aur_pkgrel)

                # check if version is different
                if str(aur_pkgver) != pkgver:
                    compare = compare_versions(aur_pkgver, pkgver)
                    if compare == -1:
                        console.print("DEBUG: Our version is newer.", style="bold blue")
                        return

                    console.print("WARNING: Version is different", style="bold red")
                    # create_issue(owner, "CachyOS-PKGBUILDs", pkgname + ": version is different", "Version is different for " + pkgname + ".\n\nCachyOS: " + pkgver + "-" + pkgrel + "\nAUR: " + aur_pkgver + "-" + aur_pkgrel + "\n\nPlease update the package. \n\n Bip bop, I'm a bot.")

                if str(aur_pkgrel) != pkgrel:
                    console.print("WARNING: Release is different", style="bold red")
            else:
                console.print("DEBUG: Does this package even exist?", style="white")

    for key, value in keys.items():
        print_pacman_separator_colored()

        # check if pkgbase is empty
        if "pkgbase" not in value:
            value["pkgname"] = value["pkgname"]
        else:
            value["pkgname"] = value["pkgbase"]

        # little treatment for pkgname without pkbase
        value["pkgname"] = value["pkgname"].split(" ")[0]
        if value["pkgname"].startswith("("):
            value["pkgname"] = value["pkgname"][1:]
        if value["pkgname"].endswith(")"):
            value["pkgname"] = value["pkgname"][:-1]

        console.print("Checking package", value["pkgname"], "version")
        # if 'url' in value:
        #    print('Checking at', value["url"])
        version = web_scrapper(value)
        console.print("CachyOS:", value["pkgver"])
        console.print("Upstream:", version)

        # check  if version is not None
        if version is None:
            console.print("DEBUG: Upstream version not found.", style="white")
            console.print(
                "DEBUG: Quiting scrapper, checking ArchLinux repository.", style="white"
            )
            check_versions(key, value)

            continue
        if value["pkgver"] != version:
            compare = compare_versions(version, value["pkgver"])
            if compare == -1:
                console.print("DEBUG: Our version is newer.", style="bold blue")
                continue

            console.print("WARNING: Version is different!", style="bold red")
