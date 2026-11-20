
from Bio import Entrez
import pandas as pd
import os
import re

# NCBI requires an email for responsible API usage
Entrez.email = "3522511023@despu.edu.in"

# Search query
QUERY = """
(Alzheimer Disease[MeSH Terms]
OR Alzheimer*[Title/Abstract])
AND 2018:2026[dp]
"""

def collect_pubmed_data(max_records=150):

    print("Searching PubMed...")

    # Step 1: Search PubMed
    handle = Entrez.esearch(
        db="pubmed",
        term=QUERY,
        retmax=max_records,
        sort="relevance"
    )

    search_results = Entrez.read(handle)
    handle.close()

    pmids = search_results["IdList"]

    print("Records found:", len(pmids))

    if not pmids:
        print("No records found.")
        return

    # Step 2: Fetch article details
    print("Downloading article information...")

    handle = Entrez.efetch(db="pubmed", id=pmids, retmode="xml")
    articles = Entrez.read(handle)
    handle.close()

    # Extract the actual PubMed article records
    article_records = articles.get("PubmedArticle", [])

    print("Downloaded article records:", len(article_records))

    records = []

    for article_record in article_records:
        citation = article_record["MedlineCitation"]
        article = citation["Article"]

        pmid = str(citation["PMID"])

        title = str(article.get("ArticleTitle", ""))

        abstract_parts = article.get(
            "Abstract", {}
        ).get("AbstractText", [])

        abstract = " ".join(
            str(part) for part in abstract_parts
        )

        authors = []

        for author in article.get("AuthorList", []):
            last = author.get("LastName", "")
            initials = author.get("Initials", "")

            if last:
                authors.append(f"{last} {initials}")

        journal = article.get(
            "Journal", {}
        ).get("Title", "")

        pub_date = article.get(
            "Journal", {}
        ).get("JournalIssue", {}
        ).get("PubDate", {})

        year = pub_date.get("Year", "")

        if not year:
            medline_date = pub_date.get(
                "MedlineDate", ""
            )
            match = re.search(r"\d{4}", str(medline_date))
            year = match.group() if match else ""

        # Keep records with abstracts
        if abstract.strip():

            records.append({
                "PMID": pmid,
                "Title": title,
                "Abstract": abstract,
                "Authors": "; ".join(authors),
                "Journal": str(journal),
                "Year": str(year)
            })

    # Step 4: Save CSV
    df = pd.DataFrame(records)

    df = df.drop_duplicates(subset="PMID")

    os.makedirs("dataset", exist_ok=True)

    output_path = "dataset/pubmed_alzheimer.csv"

    df.to_csv(output_path, index=False)

    print("\nDataset collection completed!")
    print("Total articles:", len(df))
    print("Saved to:", output_path)

    return df


if __name__ == "__main__":
    collect_pubmed_data(max_records=150)
