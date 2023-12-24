# GitAPy

## Overview
GitAPy is a **NOT SO** comprehensive Python wrapper for the GitHub API. Designed to streamline interactions with GitHub repositories, it offers a range of functionalities from basic repository operations to complex integrations like pull requests and commit management.

## Features
- List repository contents
- Create, update, and delete files in a repository
- Download repository tarballs
- Manage pull requests and list commits
- Support for multiple output formats: JSON, ZIP, TAR, XML

## Installation
To install GitAPy, you need Python 3.x and the following dependencies:
- requests
- json
- rich

Clone the repository using:
```bash
git clone https://github.com/lseman/gitAPy.git
```

Then, navigate to the cloned directory and install the required packages:
```bash
pip install -r requirements.txt
```

## Usage
Run the tool from the command line using:
```bash
python gitapy.py [options] [arguments]
```

### Options:
- `-h`, `--help`: Show help message and exit
- `-v`, `--version`: Show version information
- `-l`, `--list`: List repository contents
- `-a`, `--create`: Create a new file
- `-u`, `--update`: Update an existing file
- `-d`, `--delete`: Delete an existing file
- `-t`, `--tarball`: Get repository tarball
- `-p`, `--pulls`: List pull requests
- `-c`, `--commits`: List commits

### Arguments:
- `-o`, `--owner`: Repository owner
- `-r`, `--repo`: Repository name
- `-p`, `--path`: Repository path
- `-m`, `--message`: Commit message
- `-f`, `--file`: File name
- `-s`, `--sha`: File SHA
- `-b`, `--branch`: Branch name
- `-r`, `--ref`: Reference name
- `-a`, `--archive`: Archive format
- `-t`, `--token`: GitHub personal access token
- `-v`, `--version`: GitHub API version

## License
This project is licensed under the [MIT License](LICENSE).

## Contact
For any inquiries or issues, please contact Laio O. Seman at laio [at] ieee [dot] org.
