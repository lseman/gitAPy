import spacy
import re
from bs4 import BeautifulSoup
import requests

# Load spaCy's English language model
nlp = spacy.load("en_core_web_sm")


async def extract_version_with_ner_and_regex(session, url, pkgname, current_version_format):
    try:
        headers = {'User-Agent': 'Your Custom User-Agent'}
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            text = await response.text()

            # Use current version format to create a more targeted regex
            version_regex = create_version_regex(pkgname, current_version_format)
            candidates = re.findall(version_regex, text, re.IGNORECASE)

            # Process candidates with spaCy for further refinement
            refined_candidates = []
            for candidate in candidates:
                if is_valid_version(candidate, nlp):
                    refined_candidates.append(candidate)

            return refined_candidates

    except Exception as e:
        print(f"Error during requests to {url}: {e}")
        return None

def create_version_regex(pkgname, current_version_format):
    # Create a regex pattern based on the current version format
    # Customize this function based on your specific version format
    escaped_pkgname = re.escape(pkgname)
    version_pattern = re.escape(current_version_format).replace(r'\d+', r'\d+')
    return fr"(?:Version\s*|{escaped_pkgname} )?{version_pattern}"

def is_valid_version(version, nlp):
    # Use spaCy to further validate the version
    doc = nlp(version)
    return any(ent.label_ == "CARDINAL" for ent in doc.ents)

async def main(urls, pkgname, current_version_format):
    async with ClientSession() as session:
        tasks = [extract_version_with_ner_and_regex(session, url, pkgname, current_version_format) for url in urls]
        return await asyncio.gather(*tasks)
