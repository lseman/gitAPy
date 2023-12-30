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
from src.cachy import extract_package_data
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
    subprocess.run("diff -u file_b file_a > mission", shell=True)
    with open("mission", "r") as f:
        diferenca = f.read()
    return diferenca

def find_cachy_pkgbuild(arg, folder):
    keys = {}
    for root, dirs, files in os.walk(folder):
        for name in files:
            if name == "PKGBUILD":
                if "cachy" not in name:
                    # read file and extract package data
                    with open(os.path.join(root, name), "r") as f:
                        content = f.read()
                    package_data = extract_package_data(content)
                    
                    try:
                        if package_data["pkgname"]:
                            if arg in package_data["pkgname"]:
                                return content
                    except:
                        pass

                    try:
                        if package_data["pkgbase"]:
                            if arg in package_data["pkgbase"]:
                                return content
                    except:
                        pass
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
    try:
        comando, arg = comentario_splited[index_capybara_tag].split(":")[1], comentario_splited[index_capybara_tag].split(":")[2]
        print(comando, arg)
    except:
        return

    if comando == "diff":
        # get issue title
        if os.environ.get("GITAPY_CACHE") == None:
            get_repository_tarball('CachyOS', "CachyOS-PKGBUILDs", "master", "zip")

        for root, dirs, files in os.walk("."):
            for name in dirs:
                if "CachyOS-PKGBUILDS" in name:
                    folder = name
                    break

        cachy_content = find_cachy_pkgbuild(arg, folder)

        # get the PKGBUILD file from the https://gitlab.archlinux.org/archlinux/packaging/packages/ + arg + /-/raw/main/PKGBUILD
        request = requests.get("https://gitlab.archlinux.org/archlinux/packaging/packages/" + arg + "/-/raw/main/PKGBUILD")
        # check if the request was successful
        if request.status_code == 200:
            # create a file with the PKGBUILD content
            arch_content = request.text

            if "<!DOCTYPE html>" in arch_content:
                print("Error: not in arch repos")
            else:
                diff = get_diff(arch_content, cachy_content)    
                comment_issue("CachyOS", "CachyOS-PKGBUILDs", os.environ["NUMBER"], diff)
        
        # lets try aur now
        # geting url from https://aur.archlinux.org/cgit/aur.git/plain/PKGBUILD?h= + arg
        
        request = requests.get("https://aur.archlinux.org/cgit/aur.git/plain/PKGBUILD?h=" + arg)
        # check if the request was successful
        if request.status_code == 200:
            # create a file with the PKGBUILD content
            aur_content = request.text
            if "<!DOCTYPE html>" in aur_content:
                print("Error: not in aur repos")
            else:
                diff = get_diff(aur_content, cachy_content)
                comment_issue("CachyOS", "CachyOS-PKGBUILDs", os.environ["NUMBER"], diff)

