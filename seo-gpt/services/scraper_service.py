import logging
import re
from typing import List
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException, HTTPError, Timeout

class ContentScraper:
    def __init__(self) -> None:
        pass

    def generate_list_of_pages(
        self, base_url: str, number_of_pages: int, page_param: str
    ):
        return [f"{base_url}{page_param}{i}" for i in range(1, number_of_pages + 1)]

    def search_for_pages_in_parent_page(
        self,
        base_url: str,
        path_to_search_for: str,
        root_url: str,
        paths_to_exclude: List[str],
    ) -> List[str]:
        """
        base_url is the url to start scraping from
        path_to_search_for is the URL path that the nested pages must contain
        root_url is the root where the scraped URLs will be appended to
        """
        try:
            response = requests.get(base_url, timeout=10)  # Timeout set to 10 seconds
            response.raise_for_status()  # Raises exception for HTTP errors (status code >= 400)
            soup = BeautifulSoup(response.content, "html.parser")
            links = []

            for link in soup.find_all("a"):
                href = link.get("href")
                if href and path_to_search_for in href and not any(
                    item in href for item in paths_to_exclude
                ):
                    links.append(href if "https" in href else root_url + href)
            return links

        except Timeout as e:
            logging.warning(f"Timeout occurred during request: {e}")
            return []  # Return an empty list or handle the error accordingly
        
        except HTTPError as e:
            logging.error(f"HTTP error occurred: {e}")
            return []  # Handle HTTP errors
        
        except RequestException as e:
            logging.error(f"RequestException occurred: {e}")
            return []  # Handle other request exceptions

    def scrape_all_content_under_tag(self, url: str, article_tag: str, title_tag: str):
        try:
            response = requests.get(url, timeout=10)  # Timeout set to 10 seconds
            response.raise_for_status()  # Raises exception for HTTP errors (status code >= 400)
            soup = BeautifulSoup(response.content, "html.parser")
            body = ''
            for tag in soup.find_all(article_tag):
                if tag.text is not None:
                    body += tag.text

            title = re.sub(r"[^a-zA-Z0-9\s]", "", soup.find_all(title_tag)[0].text)

            return {"body": body, "title": title}

        except Timeout as e:
            logging.warning(f"Timeout occurred during request: {e}")
            return {"body": None, "title": None}  # Handle timeout error
        
        except HTTPError as e:
            logging.error(f"HTTP error occurred: {e}")
            return {"body": None, "title": None}  # Handle HTTP errors
        
        except RequestException as e:
            logging.error(f"RequestException occurred: {e}")
            return {"body": None, "title": None}  # Handle other request exceptions

def main():
    base_url = "https://www.turquiesante.com"
    path_to_search_for = "/blog"
    root_url = "https://www.turquiesante.com"
    paths_to_exclude = ["?page=", "/disclaimer", "guidelines", "glossary"]
    number_of_pages = 5
    page_param = "?page="
    article_tag = "article"
    title_tag = "h1"

    scraper = ContentScraper()

    # Example usage
    try:
        pages = scraper.search_for_pages_in_parent_page(base_url, path_to_search_for, root_url, paths_to_exclude)
        for page in pages:
            content = scraper.scrape_all_content_under_tag(page, article_tag, title_tag)
            print(content)  # Do something with the scraped content

    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
