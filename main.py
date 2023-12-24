import os
import sys
import getopt
import requests
import json

from reading import *
from writing import *
from pr import *
from commits import *
from discord import *
# make command line arguments and help
def __main__():


    # get command line arguments
    args = sys.argv[1:]
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
        print("    -c, --create: create a new file")
        print("    -u, --update: update an existing file")
        print("    -d, --delete: delete an existing file")
        print("    -t, --tarball: get repository tarball")
        print("    -p, --pulls: list pull requests")
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
    
    try:
        options, arguments = getopt.getopt(
            sys.argv[1:], 
            "h:v:lcudtpo:r:p:m:f:s:b:r:a:t:v:jzxy", 
            [
                "help", "version", "list", "create", "update", "delete", 
                "tarball", "pulls", "owner=", "repo=", "path=", "message=", 
                "file=", "sha=", "branch=", "ref=", "archive=", "token=", 
                "json", "zip", "tar", "xml", "yaml"
            ]
        )
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)

    print(options)
    print(arguments)

    # execute option
    option = options[0][0]

    # get arguments
    options_dict = {key: value for key, value in options if key in ("-o", "--owner", "-r", "--repo", "-p", "--path", "-m", "--message", "-f", "--file")}

    owner = options_dict.get('-o') or options_dict.get('--owner')
    repo = options_dict.get('-r') or options_dict.get('--repo')
    path = options_dict.get('-p') or options_dict.get('--path')
    message = options_dict.get('-m') or options_dict.get('--message')
    file = options_dict.get('-f') or options_dict.get('--file')


    print(owner, repo)
    if option in ("-l", "--list"):
        list_repo_contents(owner, repo)
    elif option in ("-c", "--create"):
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

    __main__()