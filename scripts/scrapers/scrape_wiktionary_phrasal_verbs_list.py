from typing import Optional

import requests
from bs4 import BeautifulSoup

PATH_TO_DUMP = "../../smart_word_hints_api/app/assets/english_phrasal_verbs.txt"
URL = "https://en.wiktionary.org"
START_PAGE = f"{URL}/wiki/Category:English_phrasal_verbs"


def extract_verbs(soup: BeautifulSoup) -> set[str]:
    verbs = set()
    bullet_points_with_links = soup.find("div", id="mw-pages").findAll("li")
    for bullet_point in bullet_points_with_links:
        verbs.add(bullet_point.find("a").contents[0])
    return verbs


def find_next_page(soup: BeautifulSoup) -> Optional[str]:
    link = soup.find("a", href=True, text="next page")
    if link is None:
        return None
    return URL + link["href"]


def scrape() -> set[str]:
    verbs = set()
    page_to_request = START_PAGE
    while page_to_request is not None:
        print(f"Scraping {page_to_request}")
        soup = BeautifulSoup(requests.get(page_to_request).content, "html.parser")
        verbs |= extract_verbs(soup)
        page_to_request = find_next_page(soup)
    return verbs


def dump_to_file(verbs: list[str], path: str) -> None:
    with open(path, "w") as f:
        for item in verbs:
            f.write(f"{item}\n")


if __name__ == "__main__":
    dump_to_file(sorted(scrape()), PATH_TO_DUMP)
