
import streamlit as st
import pandas as pd
from datetime import datetime

from src.retrieval import LiteratureRetriever
from src.llm_engine import generate_answer, summarize_abstract
from src.pubmed_live import search_pubmed


# ----------------------------------
# PAGE CONFIGURATION
# ----------------------------------

st.set_page_config(
    page_title="BioResearch AI",
    page_icon="🧬",
    layout="wide"
)


# ----------------------------------
# APPLICATION TITLE
# ----------------------------------

st.title("🧬 BioResearch AI")

st.markdown(
    """
    ### Biomedical Literature Research Assistant

    Explore Alzheimer's disease research using
    Retrieval-Augmented Generation (RAG).

    Ask scientific questions, retrieve relevant research papers,
    and generate evidence-grounded summaries.
    """
)

st.divider()


# ----------------------------------
# LOAD RETRIEVAL SYSTEM
# ----------------------------------

@st.cache_resource
def load_retriever():
    return LiteratureRetriever()


try:
    with st.spinner("Loading biomedical research database..."):
        retriever = load_retriever()
        df = retriever.df

except Exception as e:
    st.error(f"Unable to load the research database: {e}")
    st.stop()


# ----------------------------------
# DATASET OVERVIEW
# ----------------------------------

total_articles = len(df)

years = pd.to_numeric(df["Year"], errors="coerce")
valid_years = years.dropna()

col1, col2, col3 = st.columns(3)

col1.metric("Total Research Articles", total_articles)

if len(valid_years) > 0:
    col2.metric(
        "Earliest Publication",
        int(valid_years.min())
    )
    col3.metric(
        "Latest Publication",
        int(valid_years.max())
    )

st.divider()


# ----------------------------------
# APPLICATION TABS
# ----------------------------------

tab1, tab2, tab3 = st.tabs([
    "🔍 Research Assistant",
    "📚 Literature Explorer",
    "📊 Dataset Analytics"
])



# ==================================
# TAB 1: RESEARCH ASSISTANT
# ==================================

with tab1:

    st.header("Ask a Research Question")

    question = st.text_area(
        "Enter your biomedical research question:",
        placeholder="Example: What is the role of amyloid beta in Alzheimer's disease?"
    )

    # Select literature source
    search_mode = st.radio(
        "Select literature source:",
        ["Local Dataset (150 Articles)", "Live PubMed Search"],
        horizontal=True
    )

        # Publication year filter for Live PubMed Search
    start_year = None
    end_year = None

    if search_mode == "Live PubMed Search":

        st.info(
            "Search PubMed dynamically for up to 50 relevant "
            "research records. Only records with abstracts "
            "will be used for retrieval."
        )

        use_year_filter = st.checkbox(
            "Filter by publication year",
            value=False
        )

        if use_year_filter:

            current_year = datetime.now().year

            year_col1, year_col2 = st.columns(2)

            with year_col1:
                start_year = st.number_input(
                    "From year",
                    min_value=1900,
                    max_value=current_year,
                    value=2020,
                    step=1
                )

            with year_col2:
                end_year = st.number_input(
                    "To year",
                    min_value=1900,
                    max_value=current_year,
                    value=current_year,
                    step=1
                )

            if start_year > end_year:
                st.error(
                    "Start year cannot be greater than end year."
                )

    top_k = st.slider(
        "Number of research articles to retrieve",
        min_value=3,
        max_value=10,
        value=5
    )

    if st.button("Generate AI Answer", type="primary"):

        if not question.strip():
            st.warning("Please enter a research question.")

        else:
            try:

                # ----------------------------------
                # LOCAL DATASET RETRIEVAL
                # ----------------------------------

                if search_mode == "Local Dataset (150 Articles)":

                    with st.spinner(
                        "Searching the local research database..."
                    ):

                        results = retriever.search(
                            question,
                            top_k=top_k
                        )

                # ----------------------------------
                # LIVE PUBMED RETRIEVAL
                # ----------------------------------

                else:

                    with st.spinner(
                        "Searching PubMed for research articles..."
                    ):

                        live_df = search_pubmed(
                            query=question,
                            max_results=50,
                            start_year=start_year,
                            end_year=end_year
                        )

                    if live_df.empty:

                        st.warning(
                            "No PubMed articles with abstracts "
                            "were found. Try a different query."
                        )

                        st.stop()

                    with st.spinner(
                        "Building TF-IDF index and ranking articles..."
                    ):

                        live_retriever = LiteratureRetriever(
                            dataframe=live_df
                        )

                        results = live_retriever.search(
                            question,
                            top_k=top_k
                        )

                # ----------------------------------
                # GENERATE AI RESPONSE
                # ----------------------------------

                with st.spinner("Generating AI response..."):

                    answer = generate_answer(
                        question,
                        results
                    )

                # Save results in session state

                st.session_state["answer"] = answer
                st.session_state["results"] = results
                st.session_state["question"] = question
                st.session_state["search_mode"] = search_mode

            except Exception as e:

                st.error(f"An error occurred: {e}")

    # ----------------------------------
    # DISPLAY AI ANSWER
    # ----------------------------------

    if "answer" in st.session_state:

        st.subheader("AI-Generated Research Answer")

        st.caption(
            f"Literature source: {st.session_state['search_mode']}"
        )

        st.markdown(st.session_state["answer"])

        st.caption(
            "Answers are generated from retrieved abstracts "
            "and should be independently verified."
        )

        st.divider()

        # ----------------------------------
        # DISPLAY RETRIEVED ARTICLES
        # ----------------------------------

        st.subheader("Retrieved Research Articles")

        results = st.session_state["results"]

        for _, row in results.iterrows():

            with st.expander(str(row["Title"])):

                st.write(
                    "**PMID:**",
                    row.get("PMID", "Not available")
                )

                st.write(
                    "**Relevance Score:**",
                    round(row["Relevance_Score"], 4)
                )

                if "Journal" in row.index:
                    st.write("**Journal:**", row.get("Journal", ""))

                if "Publication_Date" in row.index:
                    st.write(
                        "**Publication Date:**",
                        row.get("Publication_Date", "")
                    )

                st.write("**Abstract:**")
                st.write(row["Abstract"])

                pmid = row.get("PMID")

                if pd.notna(pmid):
                    st.markdown(
                        f"[View on PubMed](https://pubmed.ncbi.nlm.nih.gov/{pmid}/)"
                    )


# ==================================
# TAB 2: LITERATURE EXPLORER
# ==================================

with tab2:

    st.header("Explore Biomedical Literature")

    search_query = st.text_input(
        "Search research articles:",
        placeholder="Example: tau protein and Alzheimer's disease"
    )

    if st.button("Search Literature"):

        if not search_query.strip():
            st.warning("Enter a search term.")

        else:
            try:
                search_results = retriever.search(
                    search_query,
                    top_k=5
                )

                st.session_state["explorer_results"] = search_results

            except Exception as e:
                st.error(f"Search failed: {e}")

    if "explorer_results" in st.session_state:

        for index, row in st.session_state["explorer_results"].iterrows():

            with st.expander(
                f"{row['Title']} | PMID: {row['PMID']}"
            ):

                st.write("**Publication Year:**", row["Year"])

                st.write(
                    "**Relevance Score:**",
                    round(row["Relevance_Score"], 4)
                )

                st.write("**Abstract:**")
                st.write(row["Abstract"])

                st.markdown(
                    f"[Read article on PubMed](https://pubmed.ncbi.nlm.nih.gov/{row['PMID']}/)"
                )

                summary_key = f"summary_{row['PMID']}"

                if st.button(
                    "Summarize Abstract",
                    key=f"summarize_{row['PMID']}"
                ):

                    try:
                        with st.spinner("Summarizing abstract..."):

                            summary = summarize_abstract(
                                row["Title"],
                                row["Abstract"],
                                row["PMID"]
                            )

                        st.session_state[summary_key] = summary

                    except Exception as e:
                        st.error(f"Summarization failed: {e}")

                if summary_key in st.session_state:
                    st.markdown("**AI Abstract Summary**")
                    st.markdown(st.session_state[summary_key])


# ==================================
# TAB 3: DATASET ANALYTICS
# ==================================

with tab3:

    st.header("Research Dataset Analytics")

    st.subheader("Publication Distribution by Year")

    year_data = pd.to_numeric(
        df["Year"],
        errors="coerce"
    ).dropna()

    if not year_data.empty:

        year_counts = (
            year_data.astype(int)
            .value_counts()
            .sort_index()
        )

        st.bar_chart(year_counts)

    else:
        st.info("Publication year information is unavailable.")

    st.divider()

    st.subheader("Dataset Preview")

    st.dataframe(
        df[["PMID", "Title", "Journal", "Year"]],
        use_container_width=True
    )

    st.download_button(
        label="Download Research Dataset",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="pubmed_alzheimer.csv",
        mime="text/csv"
    )


# ----------------------------------
# FOOTER
# ----------------------------------

st.divider()

st.caption(
    "BioResearch AI | Academic Mini Project | "
    "Powered by PubMed, TF-IDF, Cosine Similarity and Groq GPT-OSS"
)
