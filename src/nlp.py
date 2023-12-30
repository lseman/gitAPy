import spacy
import re
from bs4 import BeautifulSoup
import requests
import random
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
    """
    Extracts version numbers from a webpage using NER and regex.

    Args:
        url (str): URL of the webpage.
        pkgname (str): Name of the package.

    Returns:
        str or None: Extracted version number, if found.
    """

    # first filter the url to get the webpage
    #print( "url: ", url)
    
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    text = soup.get_text()
    #print( "text: ", text)
    
    candidates = []
    # Using spaCy NER to find potential version numbers
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "CARDINAL":  # 'CARDINAL' often represents numbers in spaCy
            version = extract_version_from_text(ent.text, pkgname)
            #print( "version: ", version)
            if version:
                candidates.append(version)
                

    # Fallback to regex if NER doesn't find anything
    version = extract_version_from_text(text, pkgname)
    if version:
        candidates.append(version)
    #print( "version: ", version)
    return candidates

def extract_version_from_text(text, pkgname):
    """
    Extracts version number from text using regular expressions.

    Args:
        text (str): Text to search within.
        pkgname (str): Name of the package.

    Returns:
        str or None: Extracted version number, if found.
    """
    escaped_pkgname = re.escape(pkgname)
    version_regex = r"(?:Version\s*|{} )?v?\d+\.\d+(?:\.\d+)*(?:-\w+)?".format(escaped_pkgname)
    match = re.search(version_regex, text, re.IGNORECASE)
    if match:
        return match.group().split(" ")[-1]  # Return only the version number
    return None


