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
from src.utils import _display_json
# import console from rich
from rich.console import Console
from src.scrapper import *

import base64
import subprocess

import subprocess

def get_diff(a, b):
    # Write a and b to files
    with open("file_a", "w") as f:
        f.write(a)
    with open("file_b", "w") as f:
        f.write(b)
    
    # Execute diff -u on the files
    diff = subprocess.run(["diff", "-u", "file_a", "file_b"], capture_output=True)
    
    return diff.stdout.decode("utf-8")


def do_watch():
    # get os.environ NUMBER, which represents issue number
    #issue_number = 93

    #issue = get_issue('CachyOS', 'CachyOS-PKGBUILDS', issue_number)
    #_display_json(issue)

    # read COMENTARIO from so.environ COMENTARIO
    issue_number = os.environ["NUMBER"]
    comentario = os.environ["COMENTARIO"]

    # find the #capybara tag in the comentario
    capybara_tag = "#capybara"
    comentario_splited = comentario.split(" ")
    #print(comentario_splited)
    # get the index in comentario splited in which #capybara is contained
    index_capybara_tag = next((i for i, s in enumerate(comentario_splited) if capybara_tag in s), None)
    #print(index_capybara_tag)
    comando, arg = comentario_splited[index_capybara_tag].split(":")[1], comentario_splited[index_capybara_tag].split(":")[2]
    print(comando, arg)


    if comando == "diff":
        # get issue title
        if os.environ.get("GITAPY_CACHE") == None:
            get_repository_tarball('CachyOS', "CachyOS-PKGBUILDs", "master", "zip")

        for root, dirs, files in os.walk("."):
            for name in dirs:
                if "CachyOS-PKGBUILDS" in name:
                    folder = name
                    break

        for root, dirs, files in os.walk(folder):
            for name in dirs:
                if arg in name:
                    folder_pkg = name
                    break

        # get cachy pkgbuild content
        with open(folder + "/" + folder_pkg + "/PKGBUILD", "r") as f:
            cachy_content = f.read()

        #print(cachy_content)

        # get the PKGBUILD file from the https://gitlab.archlinux.org/archlinux/packaging/packages/ + arg + /-/raw/main/PKGBUILD
        request = requests.get("https://gitlab.archlinux.org/archlinux/packaging/packages/" + arg + "/-/raw/main/PKGBUILD")
        # check if the request was successful
        if request.status_code == 200:
            # create a file with the PKGBUILD content
            arch_content = request.text
            diff = get_diff(arch_content, cachy_content)
            
            comment_issue("CachyOS", "CachyOS-PKGBUILDs", os.environ["NUMBER"], diff)
        else:
            print("Error: ", request.status_code)
        
        # lets try aur now
        # geting url from https://aur.archlinux.org/cgit/aur.git/plain/PKGBUILD?h= + arg
        
        request = requests.get("https://aur.archlinux.org/cgit/aur.git/plain/PKGBUILD?h=" + arg)
        # check if the request was successful
        if request.status_code == 200:
            # create a file with the PKGBUILD content
            aur_content = request.text
            diff = get_diff(aur_content, cachy_content)
            comment_issue("CachyOS", "CachyOS-PKGBUILDs", os.environ["NUMBER"], diff)

        else:
            print("Error: ", request.status_code)

