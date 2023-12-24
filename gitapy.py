import os
import sys
import getopt
import requests
import json

from src.reading import *
from src.writing import *
from src.pr import *
from src.commits import *
from src.discord import *
from src.cachy import *

# read config file
def read_config():
    # read definitions from .env file
    with open(".config", "r") as f:
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
def __main__():
    # get command line arguments
    args = sys.argv[1:]

    # read config file
    read_config()

    # check if there are any arguments
    if len(args) == 0:
        
        print('GitAPy - A Python wrapper for the GitHub API')
        print('Usage: gitapy.py [options] [arguments]')
        print('Use "gitapy.py --help" for more information.')
        print('Author: Laio O. Seman')
        print('Email: laio [at] ieee [dot] org')
        sys.exit(1)

        print("Usage: gitapy.py [options] [arguments]")
        print("Options:")
        print("    -h, --help: show this help message and exit")
        print("    -v, --version: show version information and exit")
        print("    -l, --list: list repository contents")
        print("    -a  --create: create a new file")
        print("    -u, --update: update an existing file")
        print("    -d, --delete: delete an existing file")
        print("    -t, --tarball: get repository tarball")
        print("    -p, --pulls: list pull requests")
        print("    -c, --commits: list commits")
        print("Arguments:")
        print("    -o, --owner: repository owner")
        print("    -r, --repo: repository name")
        print("    -p, --path: repository path")
        print("    -m, --message: commit message")
        print("    -f, --file: file name")
        print("    -s, --sha: file SHA")
        print("    -b, --branch: branch name")
        print("    -r, --ref: reference name")
        print("    -a, --archive: archive format")
        print("    -t, --token: GitHub personal access token")
        print("    -v, --version: GitHub API version")
        print("    -j, --json: output in JSON format")
        print("    -z, --zip: output in ZIP format")
        print("    -r, --tar: output in TAR format")
        print("    -x, --xml: output in XML format")
        print("    -y, --yaml: output in YAML format")

    # create getopt function

    all_options = ["help", "version", "list", "add", "update", "delete", 'commits', 'pulls', 'tarball']

    all_arguments = ["owner", "repo", "path", "message", "file", "sha", "branch", "ref", "archive", "token", "version", "json", "zip", "tar", "xml", "yaml"]
    all_arguments_cmd = ['-' + str[0] for str in all_arguments]

    options = sys.argv[1:]
    option=args[0]

    # to find owner, the index which value is -o or --owner
    # for each arguments in argument, create a variable with the item name and the value of the next item
    for i in range(len(args)):
        if args[i] in all_arguments_cmd:
            # get index of args[i] in all_arguments_cmd
            index = all_arguments_cmd.index(args[i])
            globals()[all_arguments[index]] = args[i+1]
        else:
            continue

    if option in ("-l", "--list"):
        list_repo_contents(owner, repo)
    elif option in ("-c", "--commits"):
        list_commits(owner, repo)
    elif option in ("-a", "--add"):
        put_repo_contents(owner, repo, path, message, file)
    elif option in ("-u", "--update"):
        put_repo_contents(owner, repo, path, message, file, sha)
    elif option in ("-d", "--delete"):
        del_repo_contents(owner, repo, path, message, sha)
    elif option in ("-t", "--tarball"):
        get_repo_tarball(owner, repo, ref, archive)
    elif option in ("-p", "--pulls"):
        list_pull_requests(owner, repo)
    else:
        print("Error: invalid option")
        sys.exit(1)

if __name__ == "__main__":

    # check if first arg is cachy
    if sys.argv[1] == 'cachy':
        # call cachy function
        read_config()
        cachy()
    elif sys.argv[1] == 'up':
        # call cachy function
        read_config()
        cachy_update()
    else:
        # call main function
        __main__()
