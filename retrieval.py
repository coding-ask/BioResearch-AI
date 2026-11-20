

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    from .preprocessing import load_and_clean_data
except ImportError:
    from preprocessing import load_and_clean_data


class LiteratureRetriever:

    def __init__(self, dataframe=None):

        # Load the existing dataset if no DataFrame is provided
        if dataframe is None:
            self.df = load_and_clean_data()
            self.source = "Local Dataset"
        else:
            self.df = dataframe.copy()
            self.source = "Live PubMed"

        # Validate required columns
        required_columns = ["Title", "Abstract"]

        for column in required_columns:
            if column not in self.df.columns:
                raise ValueError(
                    f"Missing required column: {column}"
                )

        # Clean text fields
        self.df["Title"] = self.df["Title"].fillna("").astype(str)
        self.df["Abstract"] = self.df["Abstract"].fillna("").astype(str)

        # Remove records without abstracts
        self.df = self.df[
            self.df["Abstract"].str.strip() != ""
        ].copy()

        self.df = self.df.reset_index(drop=True)

        if self.df.empty:
            raise ValueError(
                "No articles with abstracts are available."
            )

        # Combine title and abstract
        self.documents = (
            self.df["Title"] + " " +
            self.df["Abstract"]
        ).tolist()

        # Convert documents into TF-IDF vectors
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=5000
        )

        self.tfidf_matrix = self.vectorizer.fit_transform(
            self.documents
        )

        print(f"TF-IDF indexing completed! Source: {self.source}")
        print(f"Total indexed articles: {len(self.df)}")

    def search(self, query, top_k=5):

        if not query or not query.strip():
            raise ValueError("Please enter a research question.")

        # Convert query into TF-IDF vector
        query_vector = self.vectorizer.transform([query])

        # Calculate cosine similarity
        similarity_scores = cosine_similarity(
            query_vector,
            self.tfidf_matrix
        ).flatten()

        # Get top matching articles
        top_indices = similarity_scores.argsort()[::-1][:top_k]

        results = self.df.iloc[top_indices].copy()
        results["Relevance_Score"] = similarity_scores[top_indices]

        return results


if __name__ == "__main__":

    print("Starting literature retrieval...")

    retriever = LiteratureRetriever()

    question = "What is the role of amyloid beta in Alzheimer's disease?"

    results = retriever.search(question, top_k=5)

    print("\nTop 5 Relevant Research Articles:\n")

    for _, row in results.iterrows():
        print("Title:", row["Title"])
        print("PMID:", row.get("PMID", "Not available"))
        print("Relevance:", round(row["Relevance_Score"], 4))
        print("-" * 60)
