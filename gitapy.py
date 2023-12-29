import os
import sys
import getopt
import requests
import json
import inspect

import src.reading
import src.commits
import src.pr
import src.db
import src.utils
import src.caching

from src.reading import *
from src.commits import *
from src.pr import *
from src.db import *
from src.utils import *
from src.fork import *
from src.caching import _get_owner_list, _update_owner_list
from src.cachy import *

# import _ functions also
from src.reading import _get_owner_repositories
from src.utils import _prettify

from rich import print as rprint

import subprocess


def _get_xdg_config_home():
    if os.environ.get("XDG_CONFIG_HOME") != None:
        XDG_CONFIG_HOME = os.environ["XDG_CONFIG_HOME"] + "/gitapy/"
    else:
        XDG_CONFIG_HOME = os.environ["HOME"] + "/.config/gitapy/"
    return XDG_CONFIG_HOME


def _get_cache(cache_kind):
    cache_path = _get_xdg_config_home() + "cache/" + cache_kind + ".txt"
    with open(cache_path, "r") as f:
        cache = f.read()

    # split lines and make a list encoded to gum
    cache = cache.splitlines()
    cache = "\n".join(cache)
    return cache


# read config file
def read_config():
    # get config from XDG_CONFIG_HOME
    if os.environ.get("XDG_CONFIG_HOME") != None:
        config_path = os.environ["XDG_CONFIG_HOME"] + "/gitapy/config"
    else:
        config_path = os.environ["HOME"] + "/.config/gitapy/config"

    # read definitions from .env file
    with open(config_path, "r") as f:
        for line in f:
            if line.startswith("#"):
                continue
            else:
                key, value = line.strip().split("=")

                # remove whitespaces
                key = key.strip()
                value = value.strip()
                os.environ[key] = value


# make command line arguments and help
def _cmd():
    # get command line arguments
    args = sys.argv[1:]

    # read config file
    read_config()

    # check if there are any arguments
    if len(args) == 0 or args[0] in ("-h", "--help"):
        rprint("GitAPy - A Python wrapper for the GitHub API", ":vampire:")
        rprint("Usage: gitapy.py [options] [arguments]")
        rprint("")
        rprint('Use "gitapy.py --help" for more information.')
        rprint("Author: Laio O. Seman")
        rprint("Email: laio@ieee.org")
        if len(args) == 0:
            sys.exit(0)
        rprint("")
        rprint("Usage: gitapy.py [options] [arguments]")
        rprint("")
        rprint("Options:")
        rprint("    -h, --help: show this help message and exit")
        rprint("    -v, --version: show version information and exit")
        rprint("    -l, --list: list repository contents")
        rprint("    -a  --create: create a new file")
        rprint("    -u, --update: update an existing file")
        rprint("    -d, --delete: delete an existing file")
        rprint("    -t, --tarball: get repository tarball")
        rprint("    -p, --pulls: list pull requests")
        rprint("    -c, --commits: list commits")
        rprint("    -s, --sync: sync fork with upstream")
        rprint("")
        rprint("Arguments:")
        rprint("    -o, --owner: repository owner")
        rprint("    -r, --repo: repository name")
        rprint("    -p, --path: repository path")
        rprint("    -m, --message: commit message")
        rprint("    -f, --file: file name")
        rprint("    -s, --sha: file SHA")
        rprint("    -r, --ref: reference name")
        rprint("    -j, --json: output in JSON format")
        rprint("    -z, --zip: output in ZIP format")
        rprint("    -r, --tar: output in TAR format")
        rprint("    -z, --extra options: extra options")
        sys.exit(1)

    # create getopt function

    all_options = ["help", "version", "list", "add", "update", "delete", "commits", "pulls", "tarball"]

    all_arguments = [
        "owner",
        "repo",
        "number",
        "path",
        "message",
        "file",
        "sha",
        "branch",
        "ref",
        "archive",
        "token",
        "version",
        "json",
        "zip",
        "tar",
        "xtra",
    ]
    all_arguments_cmd = ["-" + str[0] for str in all_arguments]

    options = sys.argv[1:]
    option = args[0]

    # to find owner, the index which value is -o or --owner
    # for each arguments in argument, create a variable with the item name and the value of the next item
    for i in range(len(args)):
        if args[i] in all_arguments_cmd:
            # get index of args[i] in all_arguments_cmd
            index = all_arguments_cmd.index(args[i])
            globals()[all_arguments[index]] = args[i + 1]
            if args[i] == "-o" or args[i] == "--owner":
                _update_owner_list(args[i + 1])
        else:
            continue


    if option in ("-l", "--list"):
        list_repository_contents(owner, repo)
    elif option in ("-c", "--commits"):
        list_repository_commits(owner, repo)
    elif option in ("-a", "--add"):
        add_repository_content(owner, repo, path, message, file)
    elif option in ("-u", "--update"):
        update_repository_content(owner, repo, path, message, file, sha)
    elif option in ("-d", "--delete"):
        delete_repository_content(owner, repo, path, message, sha)
    elif option in ("-t", "--tarball"):
        get_repository_tarball(owner, repo, ref, archive)
    elif option in ("-p", "--pulls"):
        list_pull_requests(owner, repo)
    elif option in ("-i", "--info"):
        get_pull_request(owner, repo, number, xtra)
    elif option in ("-s", "--sync"):
        merge_fork_upstream(owner, repo, branch)
    else:
        # handle other options or show an error
        rprint("Error: Invalid option")


if __name__ == "__main__":

    # check if no arguments were passed, if so, start iteractive mode
    # if len(sys.argv) >= 2:
    
    if (len(sys.argv) == 2) and (sys.argv[1] == "cachy"):
        # call cachy function
        rprint("GitAPy - A Python wrapper for the GitHub API", ":vampire:")
        rprint("v0.2 - CODNOME: vlad eater")
        rprint("Usage: gitapy.py [options] [arguments]")
        rprint("")
        rprint('Use "gitapy.py --help" for more information.')
        rprint("Author: Laio O. Seman")
        rprint("Email: laio@ieee.org")
        #read_config()
        cachy_update()
    else:
        # call main function
        _cmd()
