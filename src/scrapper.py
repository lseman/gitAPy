import requests
from src.reading import *
from bs4 import BeautifulSoup, Comment
import re
import xml.etree.ElementTree as ET
import math
from src.nlp import *

def replace_placeholders(url, pkgdata):
    """
    Replaces placeholders in the given URL with corresponding values from pkgdata.
    Continues to replace until no more placeholders are found.

    Args:
        url (str): The URL containing placeholders to be replaced.
        pkgdata (dict): A dictionary containing key-value pairs for placeholder replacement.

    Returns:
        str: The URL with all placeholders replaced by their corresponding values from pkgdata.
    """
    # Regular expression to match ${variable} or $variable
    regex = r"\$\{?(\w+)\}?"

    def replace_match(match):
        key = match.group(1)
        # Replace with value from pkgdata or keep the original placeholder if not found
        return str(pkgdata.get(key, match.group(0)))

    # Keep replacing until no more placeholders are found
    while True:
        new_url = re.sub(regex, replace_match, url)
        if new_url == url:
            break
        url = new_url

    return url

def extract_github_info(url, pkgdata):
    """
    Extracts the owner and repository name from a GitHub URL.

    Args:
        url (str): The GitHub URL.
        pkgdata (dict): Additional package data.

    Returns:
        tuple: A tuple containing the owner and repository name.

    Raises:
        ValueError: If the GitHub URL is not in the expected format.
    """
    # Replace placeholders in the URL
    url = replace_placeholders(url, pkgdata)
    url = url.split("#")[0]  # Remove any trailing anchor
    url = url.split(".git")[0]  # Remove any query parameters

    # Regex to extract owner and repo
    match = re.search(r"github\.com/([^/]+)/([^/]+)", url)

    if match:
        return match.group(1), match.group(2)  # owner, repo
    else:
        raise ValueError("GitHub URL is not in the expected format.")

def get_github_latest_release(owner, repo):
    """
    Retrieves the latest release tag name for a given GitHub repository.

    Args:
        owner (str): The owner of the GitHub repository.
        repo (str): The name of the GitHub repository.

    Returns:
        str: The latest release tag name.

    Raises:
        Exception: If the GitHub API request fails.
    """
    response = get_repository_latest_release(owner, repo)
    if response.status_code == 200:
        data = response.json()
        if data['tag_name'].startswith('v'):
            data['tag_name'] = data['tag_name'][1:]
        return data['tag_name']
    else:
        raise Exception("GitHub API request failed.")

def is_valid_version(candidate_attr, candidate_text):
    """
    Check if the given candidate attribute and text represent a valid version.

    Args:
        candidate_attr (str): The attribute associated with the candidate text.
        candidate_text (str): The text to be checked for a valid version.

    Returns:
        bool: True if the candidate attribute and text represent a valid version, False otherwise.
    """
    # Lowercase the candidate attribute string for uniform processing
    candidate_attr_lower = candidate_attr.lower()

    # Filter out known non-version patterns in the attribute
    non_version_patterns = ["initial-scale", "viewport", "charset"]
    if any(pattern in candidate_attr_lower for pattern in non_version_patterns):
        return False

    # Length check - version numbers are typically not very long
    if len(candidate_text) > 15:
        return False

    return True

def get_version_from_url(url, pkgname):
    """
    Retrieves the version number of a package from a given URL.

    Args:
        url (str): The URL to scrape for the package version.
        pkgname (str): The name of the package.

    Returns:
        str or None: The version number of the package if found, None otherwise.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    escaped_pkgname = re.escape(pkgname)

    # Extended regex to include 'Version x.x.x' format
    version_regex = r"(?:Version\s*|{} )?v?\d+\.\d+(?:\.\d+)*(?:-\w+)?".format(escaped_pkgname)
    
    def search_text_and_attributes(element):
        # Search inside the text
        text_match = re.search(version_regex, element.text, re.IGNORECASE)
        if text_match and is_valid_version(element.text, text_match.group()):
            return text_match.group().split(" ")[-1]  # Return only the version number

        # Search in the attributes
        for attr_value in element.attrs.values():
            if isinstance(attr_value, str):
                attr_match = re.search(version_regex, attr_value, re.IGNORECASE)
                if attr_match and is_valid_version(attr_value, attr_match.group()):
                    return attr_match.group().split(" ")[-1]  # Return only the version number

    # List of tags to search in
    tags_to_search = ['meta', 'div', 'span', 'a', 'p', 'footer', 'header', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']

    # Iterate over specified tags
    for tag in tags_to_search:
        for element in soup.find_all(tag):
            version = search_text_and_attributes(element)
            if version:
                return version

    return None


def pad_version(version, length):
    """
    Pads the given version list with zeros to match the specified length.

    Args:
        version (list): The version list to pad.
        length (int): The desired length of the version list.

    Returns:
        list: The padded version list.
    """
    return version + [0] * (length - len(version))

import math

def calculate_euclidean_distance(v1, v2):
    """
    Calculates the Euclidean distance between two vectors.

    Args:
        v1 (list): The first vector.
        v2 (list): The second vector.

    Returns:
        float: The Euclidean distance between the two vectors.
    """
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))

def calculate_weighted_distance(v1, v2, weights):
    """
    Calculates the weighted distance between two vectors.

    Args:
        v1 (list): The first vector.
        v2 (list): The second vector.
        weights (list): The weights for each element in the vectors.

    Returns:
        float: The weighted distance between the two vectors.
    """
    return sum(w * abs(a - b) for a, b, w in zip(v1, v2, weights))



def is_version_format_similar_weighted(found_version, current_version, threshold=10):
    """
    Checks if the format of the found version is similar to the current version,
    using a weighted distance calculation.

    Args:
        found_version (str): The version string that was found.
        current_version (str): The current version string to compare against.
        threshold (int, optional): The maximum allowed distance between the versions.
            Defaults to 10.

    Returns:
        bool: True if the format of the found version is similar to the current version,
            False otherwise.
    """
    tokenize_regex = r"(\d+)"
    found_tokens = [int(n) for n in re.findall(tokenize_regex, found_version)]
    current_tokens = [int(n) for n in re.findall(tokenize_regex, current_version)]

    # Pad versions with zeros to make them the same length
    max_length = max(len(found_tokens), len(current_tokens))
    found_tokens = pad_version(found_tokens, max_length)
    current_tokens = pad_version(current_tokens, max_length)

    # Define weights for major, minor, and patch version components
    weights = [5, 3, 1]  # we need to adjust !!!!

    # Ensure we have enough weights for all components
    weights += [1] * (max_length - len(weights))

    # Calculate weighted distance
    distance = calculate_weighted_distance(found_tokens, current_tokens, weights)
    #print(found_tokens, current_tokens, distance)

    return distance

def is_version_format_similar_euclidian(found_version, current_version, threshold=10.0):
    """
    Check if the format of the found version is similar to the current version
    using the Euclidean distance.

    Parameters:
    - found_version (str): The version string to compare.
    - current_version (str): The current version string.
    - threshold (float): The threshold value for similarity. Default is 10.0.

    Returns:
    - bool: True if the format is similar, False otherwise.
    """
    tokenize_regex = r"(\d+)"
    found_tokens = [int(n) for n in re.findall(tokenize_regex, found_version)]
    current_tokens = [int(n) for n in re.findall(tokenize_regex, current_version)]

    # Pad versions with zeros to make them the same length
    max_length = max(len(found_tokens), len(current_tokens))
    found_tokens = pad_version(found_tokens, max_length)
    current_tokens = pad_version(current_tokens, max_length)

    # Calculate Euclidean distance
    distance = calculate_euclidean_distance(found_tokens, current_tokens)
    return distance <= threshold

def get_gitlab_latest_release(custom_url, group, project):
    """
    Retrieves the latest release tag from a GitLab repository.

    Args:
        custom_url (str): The custom URL of the GitLab instance.
        group (str): The group or namespace of the repository.
        project (str): The name of the repository.

    Returns:
        str: The latest release tag.

    Raises:
        Exception: If the Atom feed cannot be fetched.
    """
    url = f"https://{custom_url}/{group}/{project}/-/tags?format=atom"
    response = requests.get(url)
    #print(response.json())
    #print(response.content)
    if response.status_code == 200:
        # Parse the XML from the response
        root = ET.fromstring(response.content)
        tags = []

        for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
            title = entry.find('{http://www.w3.org/2005/Atom}title').text
            tags.append(title)
        return tags[0]
    else:
        raise Exception("Failed to fetch Atom feed. Status Code:", response.status_code)


def extract_gitlab_info(url, pkgdata):
    """
    Extracts custom URL, group, and project information from a GitLab URL.

    Args:
        url (str): The GitLab URL.
        pkgdata (dict): A dictionary containing package data.

    Returns:
        tuple: A tuple containing the custom URL, group, and project extracted from the GitLab URL.
    """
    url = replace_placeholders(url, pkgdata)

    # Remove protocol (http:// or https://) and split the URL
    parts = url.replace('https://', '').replace('http://', '').split('/')

    custom_url = parts[0]  # Domain
    group = parts[1]  # Group
    project = parts[2]  # Project

    return custom_url, group, project

def clean_url(url):
    """
    Cleans the URL by removing unwanted parts.

    Args:
        url (str): The URL to be cleaned.

    Returns:
        str: The cleaned URL.
    """
    # Remove all .git occurrences that are not part of 'git+' protocol
    # = re.sub(r'(?<!git)\.git', '', url)
    pattern = r'\b(?:http(?:s)?://)\S+\b'
    url = re.findall(pattern, url)[0]
    # Remove unwanted characters like quotes and spaces
    url = url.replace("'", "").replace('"', '').strip().split('#')[0]

    # while there is a .git in the url, remove it
    while '.git' in url:
        url = url.replace('.git', '')

    return url

def filter_candidate(candidate):
    """
    Filters the candidate string and returns the numeric part if it contains numbers.

    Args:
        candidate (str): The candidate string to be filtered.

    Returns:
        str: The numeric part of the candidate string if it contains numbers, otherwise None.
    """
    candidate = candidate.split('-')
    candidate_incumbent = False

    for part in candidate:
        if '1' in part or '2' in part or '3' in part or '4' in part or '5' in part or '6' in part or '7' in part or '8' in part or '9' in part:
            candidate_incumbent = part
            break

    if candidate_incumbent:  
        candidate_incumbent = candidate_incumbent.split('v')[-1]
    return candidate_incumbent

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

def select_candidate(candidates, current_version, thr=10):
    """
    Selects the best candidate version.

    Args:
        candidates (list of str): Extracted candidate versions.
        current_version (str): Current version of the package.
        thr (int): Threshold for version 'distance'.

    Returns:
        str or None: The best candidate version if found, else None.
    """
    if not candidates:
        return None
    
    #print('candidates', candidates)
    #print('current_version', current_version)
    # Filter candidates greater than or equal to current version
    valid_candidates = [candidate for candidate in candidates if compare_versions(candidate, current_version) >= 0]

    # Calculate weighted 'distance' for each candidate
    candidates_weight = [(candidate, is_version_format_similar_weighted(candidate, current_version)) for candidate in valid_candidates]

    # Filter based on threshold and select the best candidate
    filtered_candidates = [candidate for candidate, weight in candidates_weight if weight <= thr]

    if filtered_candidates:
        # Select the candidate with the maximum weight (still under the threshold)
        return max(filtered_candidates, key=lambda c: is_version_format_similar_weighted(c, current_version))

    return None


def web_scrapper(pkgdata):
    """
    Scrape the web to find the latest release candidate for a given package.

    Args:
        pkgdata (dict): A dictionary containing package information.

    Returns:
        str: The latest release candidate for the package, or None if not found.
    """
    thr = 10
    visited = []
    for source in ([pkgdata["url"]] + pkgdata["source"]):
        if source == '${source[@]}':
            continue
        source = replace_placeholders(source, pkgdata)
        try:
            source = clean_url(source)
        except:
            continue
        print('source', source)
        if source in visited:
            continue
        visited.append(source)
       
        try:
            if 'gitlab' in source:
                custom_url, group, repo = extract_gitlab_info(source, pkgdata)
                custom_url = custom_url.replace('"', '').replace("'", '').replace('(', '').replace(')', '')
                candidate = get_gitlab_latest_release(custom_url, group, repo)
                if  candidate:
                    candidate = filter_candidate(candidate)
                if candidate and (is_version_format_similar_weighted(candidate, pkgdata['pkgver']) <= thr):
                    return candidate
            elif "github.com" in source:
                #print('source  github', source)
                url = source.strip("()'")
                owner, repo = extract_github_info(url, pkgdata)
                candidate = get_github_latest_release(owner, repo)
                if candidate:
                    candidate = filter_candidate(candidate)
                if candidate and (is_version_format_similar_weighted(candidate, pkgdata['pkgver']) <= thr):
                    return candidate
        except:
            pass
        #print('manual try', source)
        if 'github.com' in source:
            continue
        
        # dont follow link to files, like .zip, .tar.gz, etc
        exts_to_ignore = ['.zip', '.tar.gz', '.tar.xz', '.deb', '.rpm', '.dmg', '.exe', '.AppImage', '.pkg', '.msi', '.AppImage', '.run', '.dmg', '.exe', '.msi', '.tgz', '.jar']
        if any(ext in source for ext in exts_to_ignore):
            continue
        #try:
        try:
            candidates = extract_version_with_ner_and_regex(source, pkgdata['pkgname'])
            #print('candidates', candidates)
            if candidates != []:
                candidates = [filter_candidate(candidate) for candidate in candidates]
                try:
                    candidato = select_candidate(candidates, pkgdata['pkgver'], thr)
                except:
                    candidato = None
                if candidato:
                    return candidato
        except:
            continue
    return None
