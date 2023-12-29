import spacy
import re
from bs4 import BeautifulSoup
import requests

# Load spaCy's English language model
nlp = spacy.load("en_core_web_sm")

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


