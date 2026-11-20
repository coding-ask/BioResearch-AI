
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found. Check your .env file.")

client = Groq(api_key=api_key)

MODEL_NAME = "openai/gpt-oss-120b"


def generate_answer(question, retrieved_articles):

    context = ""

    for _, row in retrieved_articles.iterrows():
        abstract = str(row["Abstract"])[:1200]

        context += f"""
Title: {row['Title']}
PMID: {row['PMID']}
Abstract: {abstract}
"""

    system_prompt = """
You are BioResearch AI, a biomedical literature research assistant.

Answer using ONLY the supplied research abstracts.

Instructions:
1. Write clear scientific explanations.
2. Do not invent findings, mechanisms, genes or proteins.
3. Cite relevant claims using the supplied PMIDs.
4. Distinguish hypotheses from established findings when possible.
5. If the evidence is insufficient, state that clearly.
6. Do not provide medical diagnosis or treatment advice.
"""

    user_prompt = f"""
Research question:
{question}

Retrieved research articles:
{context}

Generate an evidence-based answer with relevant PMID citations.
"""

    response = client.chat.completions.create(
    model=MODEL_NAME,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    temperature=0.2,
    max_completion_tokens=900
)

    return response.choices[0].message.content


def summarize_abstract(title, abstract, pmid):

    prompt = f"""
Summarize the following biomedical research abstract.

Title: {title}
PMID: {pmid}

Abstract:
{abstract}

Provide the summary under these headings:
1. Research Objective
2. Methodology
3. Main Findings
4. Conclusion

Use only information explicitly present in the abstract.
Do not invent missing information.
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "You are a biomedical literature summarization assistant."
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content


if __name__ == "__main__":

    try:
        from .retrieval import LiteratureRetriever
    except ImportError:
        from retrieval import LiteratureRetriever

    retriever = LiteratureRetriever()

    question = "What is the role of amyloid beta in Alzheimer's disease?"

    results = retriever.search(question, top_k=5)

    print("\nGenerating AI response...\n")
    print(generate_answer(question, results))
