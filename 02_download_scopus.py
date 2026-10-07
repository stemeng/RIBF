"""
Download Scopus article records for one journal identified by one ISSN.

This script is a simplified version of the retrieval code used in the paper.
It retrieves article-level Scopus records for a single journal-year range and
saves one CSV file. Raw abstracts are downloaded only for users with lawful
Scopus API access.

Before running, set your Scopus API key as an environment variable:

    Windows PowerShell:
        $env:SCOPUS_API_KEY = "your_api_key_here"

    macOS/Linux:
        export SCOPUS_API_KEY="your_api_key_here"
"""

import os
import time

import pandas as pd
import requests


# ---------------------------------------------------------------------
# User settings
# ---------------------------------------------------------------------

JOURNAL = "JF"
ISSN = "0022-1082"
START_YEAR = 1996
END_YEAR = 2025
OUTPUT_FILE = "scopus_one_journal_download.csv"


# ---------------------------------------------------------------------
# Scopus API settings
# ---------------------------------------------------------------------

API_KEY = os.getenv("SCOPUS_API_KEY")
if not API_KEY:
    raise RuntimeError("Please set the SCOPUS_API_KEY environment variable.")

SEARCH_URL = "https://api.elsevier.com/content/search/scopus"
ABSTRACT_URL = "https://api.elsevier.com/content/abstract/scopus_id/{}"

HEADERS = {
    "X-ELS-APIKey": API_KEY,
    "Accept": "application/json",
}


def as_list(value):
    """Return value as a list, preserving existing lists."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def extract_link(item, ref_type="scopus"):
    """Extract a Scopus API link from a search-result item."""
    links = item.get("link", [])
    if isinstance(links, dict):
        links = [links]

    for link in links:
        if isinstance(link, dict) and link.get("@ref") == ref_type:
            return link.get("@href")

    return None


def get_article_details(scopus_id):
    """Retrieve detailed metadata and abstract for one Scopus ID."""
    response = requests.get(
        ABSTRACT_URL.format(scopus_id),
        headers=HEADERS,
        params={"view": "FULL"},
        timeout=30,
    )

    if response.status_code != 200:
        print("Abstract retrieval error:", scopus_id, response.status_code)
        return {}

    doc = response.json().get("abstracts-retrieval-response", {}) or {}
    core = doc.get("coredata", {}) or {}

    authors = []
    author_ids = []
    authors_block = doc.get("authors") or {}
    for author in as_list(authors_block.get("author")):
        if not isinstance(author, dict):
            continue
        name = author.get("ce:indexed-name")
        auid = author.get("@auid")
        if name:
            authors.append(name)
        if auid:
            author_ids.append(auid)

    affiliations = []
    affiliation_countries = []
    for affiliation in as_list(doc.get("affiliation")):
        if not isinstance(affiliation, dict):
            continue
        affilname = affiliation.get("affilname")
        country = affiliation.get("affiliation-country")
        if affilname:
            affiliations.append(affilname)
        if country:
            affiliation_countries.append(country)

    keywords = []
    authkeywords = doc.get("authkeywords") or {}
    for keyword in as_list(authkeywords.get("author-keyword")):
        if isinstance(keyword, dict):
            keyword = keyword.get("$")
        if keyword:
            keywords.append(keyword)

    return {
        "abstract": core.get("dc:description"),
        "n_citations": core.get("citedby-count"),
        "publication_name": core.get("prism:publicationName"),
        "volume": core.get("prism:volume"),
        "issue": core.get("prism:issueIdentifier"),
        "pages": core.get("prism:pageRange"),
        "cover_date": core.get("prism:coverDate"),
        "publisher": core.get("dc:publisher"),
        "subtype": core.get("subtype"),
        "subtype_description": core.get("subtypeDescription"),
        "authors": "; ".join(authors),
        "author_ids": "; ".join(author_ids),
        "affiliations": "; ".join(sorted(set(affiliations))),
        "affiliation_countries": "; ".join(sorted(set(affiliation_countries))),
        "keywords": "; ".join(keywords),
    }


def download_one_journal(journal, issn, start_year, end_year):
    """Download Scopus records for one journal and one ISSN."""
    results = []

    for year in range(start_year, end_year + 1):
        print(f"Downloading {journal} ({issn}) - {year}")
        start = 0

        while True:
            query = f"ISSN({issn}) AND PUBYEAR = {year} AND DOCTYPE(ar)"
            params = {
                "query": query,
                "count": 25,
                "start": start,
                "view": "COMPLETE",
            }

            try:
                response = requests.get(
                    SEARCH_URL,
                    headers=HEADERS,
                    params=params,
                    timeout=30,
                )
            except requests.exceptions.RequestException as exc:
                print("Search request error:", journal, year, exc)
                break

            if response.status_code != 200:
                print("Search error:", journal, year, response.status_code)
                print(response.text)
                break

            search_results = response.json().get("search-results", {}) or {}
            entries = search_results.get("entry", [])
            total = int(search_results.get("opensearch:totalResults", 0))

            print(f"  {total} records")
            if not entries:
                break

            for item in entries:
                scopus_id = item.get("dc:identifier", "").replace("SCOPUS_ID:", "")
                if not scopus_id:
                    continue

                details = get_article_details(scopus_id)
                results.append(
                    {
                        "journal": journal,
                        "query_issn": issn,
                        "year": year,
                        "scopus_id": scopus_id,
                        "doi": item.get("prism:doi"),
                        "title": item.get("dc:title"),
                        "eid": item.get("eid"),
                        "scopus_link": extract_link(item, "scopus"),
                        "abstract_link": extract_link(item, "self"),
                        **details,
                    }
                )

                time.sleep(0.3)

            start += 25
            if start >= total:
                break

        time.sleep(1)

    return pd.DataFrame(results)


if __name__ == "__main__":
    data = download_one_journal(JOURNAL, ISSN, START_YEAR, END_YEAR)

    if not data.empty:
        data_with_doi = data[data["doi"].notna()].drop_duplicates(subset="doi")
        data_without_doi = data[data["doi"].isna()].drop_duplicates(subset="scopus_id")
        data = pd.concat([data_with_doi, data_without_doi], ignore_index=True)

    data.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    print(f"Saved {len(data)} records to {OUTPUT_FILE}")
