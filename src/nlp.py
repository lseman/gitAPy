import spacy
import re
from bs4 import BeautifulSoup
import requests
import random
import time
from urllib.parse import urljoin
# Load spaCy's English language model
nlp = spacy.load("en_core_web_sm")

def randomize_header():
    """
    Randomizes the user agent header.

    Returns:
        dict: Randomized header.
    """
    # Randomize the user agent header

    possible_user_agents = [
        # Chrome
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
        # Firefox
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:55.0) "
        "Gecko/20100101 Firefox/55.0",
        # Firefox
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) "
        "Gecko/20100101 Firefox/54.0",
        # Edge
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",
        # Edge
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",
        # Edge
        "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",
        # Internet Explorer
        "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) "
        "like Gecko",
        # Internet Explorer
        "Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko",
        # Internet Explorer
        "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) "
        "like Gecko",
        # Opera
        "Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14",
        # Opera
        "Opera/9.80 (Windows NT 6.1; WOW64) Presto/2.12.388 Version/12.18",
        # Safari
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
        ]

    return {'User-Agent': possible_user_agents[random.randint(0, len(possible_user_agents) - 1)]}

def extract_version_with_ner_and_regex(url, pkgname):
    session = requests.Session()
    session.headers.update(randomize_header())
    
    response = session.get(url)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    text = soup.get_text()

    candidates = extract_versions(text, pkgname)

    # Broadening search for download links
    link_keywords = ["Download", "Latest version", "Update", "Release"]
    link_regex = re.compile("|".join(link_keywords), re.IGNORECASE)

    for a in soup.find_all('a', string=link_regex):
        download_link = urljoin(url, a['href'])  # Handle relative URLs
        download_response = session.get(download_link)
        if download_response.status_code == 200 and 'text' in download_response.headers.get('Content-Type', ''):
            download_text = BeautifulSoup(download_response.content, 'html.parser').get_text()
            candidates.extend(extract_versions(download_text, pkgname))

        time.sleep(1)  # Simple rate limiting

    return list(set(candidates))  # Remove duplicates

def extract_versions(text, pkgname):
    candidates = []
    doc = nlp(text)  # Assuming you have an NLP model for entity recognition
    for ent in doc.ents:
        if ent.label_ == "CARDINAL":
            version = extract_version_from_text(ent.text, pkgname)
            if version:
                candidates.append(version)

    version = extract_version_from_text(text, pkgname)
    if version:
        candidates.append(version)
    return candidates

def extract_version_from_text(text, pkgname):
    escaped_pkgname = re.escape(pkgname)
    version_regex = r"(?:Version\s*|{} )?v?\d+\.\d+(?:\.\d+)*(?:-\w+)?".format(escaped_pkgname)
    match = re.search(version_regex, text, re.IGNORECASE)
    if match:
        return match.group().split(" ")[-1]
    return None
