
import pandas as pd
import re

def load_and_clean_data(file_path="dataset/pubmed_alzheimer.csv"):
    df = pd.read_csv(file_path)

    # Remove records with missing abstracts
    df = df.dropna(subset=["Abstract"])

    # Remove duplicate articles
    df = df.drop_duplicates(subset=["PMID"])

    # Clean abstract text
    def clean_text(text):
        text = str(text)
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"<[^>]+>", "", text)
        return text.strip()

    df["Abstract"] = df["Abstract"].apply(clean_text)
    df["Title"] = df["Title"].fillna("Untitled")

    df = df.reset_index(drop=True)

    print("Preprocessing completed!")
    print("Total articles:", len(df))

    return df


if __name__ == "__main__":
    df = load_and_clean_data()
    print(df[["PMID", "Title", "Year"]].head())
