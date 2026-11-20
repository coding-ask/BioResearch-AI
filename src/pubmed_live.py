
import requests
import xml.etree.ElementTree as ET
import pandas as pd
import time


# NCBI PubMed API endpoints
ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

HEADERS = {
    "User-Agent": "BioResearchAI/1.0 (biomedical literature research tool)"
}


def get_text(element):
    """Extract text, including text inside nested XML tags."""
    if element is None:
        return ""
    return "".join(element.itertext()).strip()


def search_pubmed(
    query,
    max_results=50,
    start_year=None,
    end_year=None
):
    """
    Search PubMed and retrieve research article details.

    Parameters:
        query (str): User's research question or search terms.
        max_results (int): Maximum number of records to retrieve.

    Returns:
        pandas.DataFrame containing PMID, Title, Abstract,
        Journal and Publication_Date.
    """

    if not query or not query.strip():
        raise ValueError("Please provide a research query.")

    # Validate publication year range
    if start_year is not None:
        start_year = int(start_year)

    if end_year is not None:
        end_year = int(end_year)

    if start_year is not None and end_year is not None:
        if start_year > end_year:
            raise ValueError(
                "Start year cannot be greater than end year."
            )

    max_results = max(1, min(int(max_results), 100))

    print(f"Searching PubMed for: {query}")

    # Step 1: Search PubMed
    search_params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "sort": "relevance",
        "retmode": "json"
    }

    # Apply publication date filter
    if start_year is not None and end_year is not None:

        search_params["mindate"] = str(start_year)
        search_params["maxdate"] = str(end_year)
        search_params["datetype"] = "pdat"

    response = requests.get(
        ESEARCH_URL,
        params=search_params,
        headers=HEADERS,
        timeout=30
    )
    response.raise_for_status()

    search_data = response.json()
    pmids = search_data["esearchresult"]["idlist"]

    if not pmids:
        print("No matching PubMed records found.")
        return pd.DataFrame(
            columns=[
                "PMID", "Title", "Abstract",
                "Journal", "Publication_Date"
            ]
        )

    print(f"Found {len(pmids)} PubMed records.")

    # Respect NCBI request frequency guidance
    time.sleep(0.4)

    # Step 2: Fetch article details
    fetch_params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml"
    }

    response = requests.get(
        EFETCH_URL,
        params=fetch_params,
        headers=HEADERS,
        timeout=60
    )
    response.raise_for_status()

    root = ET.fromstring(response.content)

    articles = []

    # Step 3: Parse article information
    for article in root.findall(".//PubmedArticle"):

        pmid = get_text(
            article.find(".//MedlineCitation/PMID")
        )

        title = get_text(
            article.find(".//Article/ArticleTitle")
        )

        abstract_parts = []

        for part in article.findall(
            ".//Article/Abstract/AbstractText"
        ):
            label = part.attrib.get("Label", "")
            text = get_text(part)

            if label:
                abstract_parts.append(f"{label}: {text}")
            else:
                abstract_parts.append(text)

        abstract = " ".join(abstract_parts)

        journal = get_text(
            article.find(".//Article/Journal/Title")
        )

        publication_date = get_text(
            article.find(
                ".//Article/Journal/JournalIssue/PubDate/Year"
            )
        )

        if not publication_date:
            publication_date = get_text(
                article.find(
                    ".//Article/Journal/JournalIssue/PubDate/MedlineDate"
                )
            )

        # Retain records with abstracts for literature retrieval
        if pmid and title and abstract:
            articles.append({
                "PMID": pmid,
                "Title": title,
                "Abstract": abstract,
                "Journal": journal,
                "Publication_Date": publication_date
            })

    df = pd.DataFrame(articles)

    if not df.empty:
        df = df.drop_duplicates(subset="PMID")
        df = df.reset_index(drop=True)

    print(f"Successfully retrieved {len(df)} articles with abstracts.")

    return df


if __name__ == "__main__":

    test_query = "Alzheimer's disease amyloid beta"

    results = search_pubmed(
        query=test_query,
        max_results=50
    )

    if not results.empty:
        results.to_csv(
            "dataset/pubmed_live_test.csv",
            index=False
        )

        print("\nFirst five retrieved articles:")
        print(results[["PMID", "Title"]].head())

        print("\nDataset saved to dataset/pubmed_live_test.csv")