# BioResearch AI

### A Retrieval-Augmented Generative AI System for Biomedical Literature Analysis

BioResearch AI is an AI-powered biomedical literature assistant developed as an MSc Bioinformatics Skill Development mini-project. It helps users explore Alzheimer's disease research literature by retrieving relevant PubMed articles and generating answers based on their abstracts.

The application combines information retrieval techniques with Generative AI to make biomedical literature exploration more accessible and efficient.

## Features

### 1. Research Assistant
- Ask biomedical research questions in natural language.
- Search a local dataset of 150 PubMed articles.
- Perform live searches using PubMed.
- Filter live search results by publication year.
- Retrieve the most relevant articles using TF-IDF and cosine similarity.
- Generate AI-powered answers with PubMed ID (PMID) references.

### 2. Literature Explorer
- Search and explore the local biomedical literature dataset.
- View article titles, abstracts and relevance scores.
- Generate structured summaries of research abstracts.

### 3. Dataset Analytics
- Explore the local dataset.
- View publication-year distributions.
- Preview the dataset.
- Download the dataset as a CSV file.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Interactive web application |
| PubMed / NCBI E-utilities | Biomedical literature retrieval |
| Pandas | Data handling and preprocessing |
| Scikit-learn | TF-IDF and cosine similarity |
| Groq API | Generative AI integration |
| GPT-OSS 120B | Answer generation and abstract summarisation |
| Requests | API communication |
| XML parsing | Processing PubMed responses |

## System Workflow

1. Collect biomedical research records from PubMed.
2. Preprocess article titles and abstracts.
3. Convert article text into TF-IDF vectors.
4. Calculate cosine similarity between the user query and article records.
5. Retrieve the top-ranked articles.
6. Pass the retrieved abstracts to the Groq-hosted GPT-OSS 120B model.
7. Generate an answer with relevant PMID references.


## Installation and Setup

### 1. Clone the repository

### 2. Navigate to the project directory

### 3. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

**Windows PowerShell**
```powershell
.venv\Scripts\Activate.ps1
```

**Linux / macOS**
```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure the Groq API key

Create a `.env` file in the project root directory:

```env
GROQ_API_KEY=your_groq_api_key
```

Obtain an API key through the Groq developer console.

### 6. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

## Research Domain

**Alzheimer's Disease**

The application focuses on biomedical literature related to:
- Amyloid-beta pathology
- Tau pathology
- Neuroinflammation
- Microglia
- Alzheimer's disease mechanisms and therapeutic research

## Limitations

- The local dataset contains a limited collection of 150 articles.
- Retrieval is based on lexical similarity using TF-IDF.
- Live PubMed retrieval considers a bounded number of candidate records per query.
- The application works primarily with article abstracts rather than full-text publications.
- Generated answers may contain unsupported interpretations and must be verified against the original publications.
- Evaluation was conducted on a small manually assessed test set.

This application is intended for academic literature exploration and is not a clinical diagnostic or treatment-support tool.

## Future Improvements

- Expand the biomedical literature dataset.
- Explore semantic and hybrid retrieval approaches.
- Improve claim-level citation verification.
- Develop a larger and independently evaluated test dataset.
- Extend support to additional biomedical research domains.