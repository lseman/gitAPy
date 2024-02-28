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
import shlex

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
    dots = white + "." * 20 + reset
    ghost = blue + "[ptr talk much when day is long]" + reset

    separator_line = pacman + dots + ghost
    print(separator_line)


def get_diff(content1, content2):
    """
    Gets the diff between two strings.

    Args:
        content1 (str): The first string.
        content2 (str): The second string.

    Returns:
        str: The diff between the two strings.
    """
    # generate temporary files
    with open("temp1", "w") as f:
        f.write(content1)
    with open("temp2", "w") as f:
        f.write(content2)

    diff = subprocess.run(["diff", "-u", "temp1", "temp2"], stdout=subprocess.PIPE)
    #subprocess.run(["diff", "-u", "temp1", "temp2"], stdout=subprocess.PIPE)
    # remove temporary files
    os.remove("temp1")
    os.remove("temp2")
    return diff.stdout.decode("utf-8")

def analyze_pkg(current, incumbent):
    # check if version is different
    if str(current) != incumbent:
        try:
            compare = compare_versions(incumbent, current)
            if compare == -1:
                console.print("DEBUG: Our version is newer.", style="bold blue")
                return
        except:
            console.print("ERROR: Bad things happened.", style="bold red")
            return


def check_issue(pkgver, issues):
    for issue in issues:
        if pkgver in issue:
            return True
    return False

def parse_source_string(source_string):
    # Strip the outer parentheses
    trimmed = source_string.strip("()")

    # Use shlex.split to correctly handle spaces within quotes
    parsed_list = shlex.split(trimmed)

    return parsed_list

def get_nix_unstable(lista):
    nix = [i for i in lista if i['repo'] == 'nix_unstable']
    return nix[0]['version']

# check repology api
def check_repology(pkgname):
    url = "https://repology.org/api/v1/projects/" + pkgname
    response = requests.get(url)
    data = response.json()
    try:
        version = get_nix_unstable(data[pkgname])
    except:
        version = None
    return version

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
    print_logo()
    console = Console()
    owner = "CachyOS"
    if os.environ.get("GITAPY_CACHE") == None:
        get_repository_tarball('CachyOS', "CachyOS-PKGBUILDs", "master", "zip")
    
    issues = list_issues("CachyOS", "CachyOS-PKGBUILDs")
    issues = [issue["title"] for issue in issues]

    for root, dirs, files in os.walk("."):
        for name in dirs:
            if "CachyOS-PKGBUILDS" in name:
                folder = name
                break

    print(folder)

    keys = {}
    for root, dirs, files in os.walk(folder):
        for name in files:
            if name == "PKGBUILD":
                try:
                    # read file and extract package data
                    print(os.path.join(root, name))
                    with open(os.path.join(root, name), "r") as f:
                        # execute bash -x PKGBUILD to get the output
                        content = f.read()
                        content_parsed = subprocess.run(
                            ["bash", "-x", os.path.join(root, name)],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True)
                    #print(content_parsed.stderr)
                    # get package data from content
                    package_data = {}
                    for line in content_parsed.stderr.splitlines():
                        if line.startswith("+ pkgbase="):
                            package_data["pkgbase"] = line.split("=")[1]
                        if line.startswith("+ pkgname="):
                            package_data["pkgname"] = line.split("=")[1]
                        if line.startswith("+ pkgver="):
                            package_data["pkgver"] = line.split("=")[1]
                        if line.startswith("+ pkgrel="):
                            package_data["pkgrel"] = line.split("=")[1]
                        if line.startswith("+ url="):
                            package_data["url"] = line.split("=")[1]
                        if line.startswith("+ source="):
                            package_data["source"] = line.split("=")[1]

                    # skip if pkgname ends with -git
                    if "-git" in package_data["pkgname"]:
                        continue
                    if "cachy" in package_data["pkgname"]:
                        continue
                    if "meta" in package_data["pkgname"]:
                        continue
                    if "nvidia" in package_data["pkgname"]:
                        continue

                    if not package_data["source"]:
                        package_data["source"] = []
                    else:
                        package_data["source"] = parse_source_string(package_data["source"])
                    package_data["content"] = content
                    # convert content to string, using newline as separator
                    package_data["content"] = "\n".join(package_data["content"])
                    keys[package_data["pkgname"]] = package_data
                except:
                    pass
    
    print(keys.keys())
    #print(pato)
    tree = create_archlinux_repo_list()

    # retrieve PKGBUILD info
    def check_versions(key, value):

        arch_ver = 0
        aur_ver = 0

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

            arch_ver = tree_version["pkgver"]
            # if second char in arch_ver is :, split it and get the second element
            if arch_ver[1] == ":":
                arch_ver = arch_ver.split(":")[1]

        console.print("DEBUG: Checking version against AUR", style="white")
        try:
            aur_version = get_package_info(key)
        except:
            aur_version = "NotFound"
        if aur_version != "NotFound":
            versioning = aur_version["Version"].split("-")
            aur_pkgver = versioning[0]
            aur_pkgrel = versioning[1]

            aur_pkgver = aur_pkgver.split(":")[-1]
            console.print("AUR", aur_pkgver, aur_pkgrel)
            aur_ver = aur_pkgver

        return arch_ver, aur_ver


    for key, value in keys.items():
        print_pacman_separator_colored()
        #print(key)
        #if key != "ripgrep":
        #    continue
        versions = []

        # check if pkgbase is empty
        if "pkgbase" not in value:
            value["pkgname"] = value["pkgname"]
        else:
            # little treatment for pkgname without pkbase
            value["pkgname"] = value["pkgname"].split(" ")[0]
            if value["pkgname"].startswith("("):
                value["pkgname"] = value["pkgname"][1:]
            if value["pkgname"].endswith(")"):
                value["pkgname"] = value["pkgname"][:-1]
            value["pkgname"] = value["pkgname"].replace("'", "")

        if "android" in value["pkgname"]:
            continue

        console.print("Checking package", value["pkgname"], "version against", value["pkgver"])
        cachy_version = value["pkgver"]


        # if 'url' in value:
        #    print('Checking at', value["url"])
        version = web_scrapper(value)
        #version = check_repology(value["pkgname"])
        console.print("CachyOS:", value["pkgver"])
        console.print("Upstream:", version)

        main_ver = version

        # check  if version is not None
        if version is None:
            console.print("DEBUG: Upstream version not found.", style="white")

        arch_ver, aur_ver = check_versions(key, value)

        # get the highest version from main_ver, arch_ver and aur_ver
        versions = [main_ver, arch_ver, aur_ver]
        # use compare_versions to get the highest version
        if main_ver is not None:
            if arch_ver != 0:
                main_versus_arch = compare_versions(main_ver, arch_ver)
                if main_versus_arch == 1:
                    highest_version = main_ver
                else:
                    highest_version = arch_ver
            else:
                highest_version = main_ver

            if aur_ver != 0:
                high_versus_aur = compare_versions(highest_version, aur_ver)
                if high_versus_aur == 1:
                    highest_version = highest_version
                else:
                    highest_version = aur_ver

        else:
            if arch_ver != 0 and aur_ver == 0:
                highest_version = arch_ver
            elif arch_ver == 0 and aur_ver != 0:
                highest_version = aur_ver
            elif arch_ver != 0 and aur_ver != 0:
                compare = compare_versions(arch_ver, aur_ver)
                if compare == 1:
                    highest_version = arch_ver
                else:
                    highest_version = aur_ver
            else:
                highest_version = None

        if highest_version is None:
            console.print("DEBUG: No version found.", style="white")
            continue

        console.print("DEBUG: Highest version found:", highest_version, style="white")

        if value["pkgver"] != highest_version:
            try:
                compare = compare_versions(highest_version, value["pkgver"])
                if compare == -1:
                    console.print("DEBUG: Our version is newer.", style="bold blue")
                    continue
                elif compare == 0:
                    console.print("DEBUG: Versions are equal after adjusting.", style="bold blue")
                    continue
            except:
                console.print("ERROR: Bad things happened.", style="bold red")
                continue

            console.print("WARNING: Version is different!", style="bold red")
            if check_issue(value['pkgname'], issues):
                console.print("DEBUG: Issue already exists, not creating another issue.", style="bold blue")
                continue
            else:
                console.print("DEBUG: Issue does not exist, creating new issue.", style="bold blue")
            
                # if version is different, open an issue
                create_issue(owner, "CachyOS-PKGBUILDs", value['pkgname'] + ": version is different", "Version is different for " + value['pkgname'] + ".\n\nCachyOS: " + value['pkgver'] + "-" + value['pkgrel'] + "\nUpstream: " + version + "\n\nPlease update the package. \n\n Bip bop, I'm a bot.")
