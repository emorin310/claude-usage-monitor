---
name: pinecone-vector-storage
description: Store and semantically search large datasets using Pinecone vector embeddings. Use when Magi needs to: (1) Index large CRA tax documents for semantic search, (2) Store and retrieve similar deductions/credits based on user situation, (3) Build searchable knowledge bases from scraped data, (4) Enable fast similarity matching across thousands of tax rules, or (5) Maintain persistent vector indexes for tax optimization queries.
---

# Pinecone Vector Storage Skill

Store large datasets as vector embeddings for fast semantic search and retrieval.

## Quick Start

### Initialize Pinecone Index

```bash
export PINECONE_API_KEY="your-api-key"
export PINECONE_ENVIRONMENT="us-west1-gcp"

python3 scripts/pinecone_store.py \
  --index tax-knowledge \
  --data cra-deductions.json \
  --action create
```

### Store CRA Data

```python
from pinecone_store import PineconeStore

store = PineconeStore(index_name="tax-knowledge")

# Store deductions with embeddings
deductions = [
    {"title": "Home Office", "description": "..."},
    {"title": "Medical Expenses", "description": "..."}
]

store.store_documents(deductions, document_type="deduction")
```

### Semantic Search

```python
from pinecone_search import PineconeSearch

search = PineconeSearch(index_name="tax-knowledge")

# Find deductions similar to user situation
results = search.find_similar(
    query="I work from home as a consultant",
    document_type="deduction",
    top_k=5
)
# Returns: [{title, similarity_score, description}, ...]
```

## Key Features

- **Semantic Search**: Find related deductions/credits by meaning, not just keywords
- **Scalable**: Index thousands of tax rules efficiently
- **Persistent**: Data survives across sessions
- **Hybrid Search**: Combine vector search with metadata filters
- **Embedding Generation**: Automatic embeddings using OpenAI models

## Architecture

```
CRA Data (JSON)
    ↓
[scrape_cra.py]
    ↓
Extract Documents
    ↓
[pinecone_store.py]
    ↓
Generate Embeddings
    ↓
Store in Pinecone
    ↓
[pinecone_search.py]
    ↓
Semantic Search Results
```

## Configuration

Set Pinecone credentials in environment:

```bash
export PINECONE_API_KEY="xxx"
export PINECONE_ENVIRONMENT="us-west1-gcp"
export PINECONE_INDEX_NAME="tax-knowledge"
export OPENAI_API_KEY="xxx"  # For embeddings
```

## Usage Patterns

### Pattern 1: Store Tax Documents

```python
store = PineconeStore(index_name="tax-knowledge")
store.store_documents(
    documents=deduction_list,
    document_type="deduction",
    metadata={"year": 2025, "province": "ontario"}
)
```

### Pattern 2: Find Similar Situations

```python
search = PineconeSearch(index_name="tax-knowledge")
results = search.find_by_situation({
    "self_employed": True,
    "home_workspace": True,
    "expenses": 5000
})
```

### Pattern 3: Suggest Deductions

```python
suggestions = search.suggest_deductions(
    income_type="self_employed",
    province="ontario",
    top_k=10
)
```

## Reference Files

See [Pinecone API Reference](references/pinecone-api.md) for detailed API documentation.

## Notes

- Requires Pinecone API key (free tier available at pinecone.io)
- Embeddings use OpenAI API (configurable model)
- Indexes are permanent and shared across sessions
- Metadata filtering improves search relevance
