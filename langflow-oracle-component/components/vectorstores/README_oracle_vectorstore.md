# Oracle Database Vector Store Component

## Overview

This custom Langflow component integrates **Oracle 23ai Vector Store** with local embeddings (no cloud dependencies) and provides configurable retrieval options for RAG (Retrieval Augmented Generation) applications.

## Features

- **Vector Storage**: Store and retrieve document embeddings using Oracle 23ai's native vector capabilities
- **Multiple Distance Metrics**: Support for COSINE, EUCLIDEAN, and DOT_PRODUCT distance strategies
- **Flexible Search Modes**:
  - **Similarity Search**: Standard vector similarity search
  - **MMR (Maximum Marginal Relevance)**: Diversity-enhanced search results
  - **Similarity Score Threshold**: Filter results by minimum relevance score
- **Local Embeddings**: Compatible with local SentenceTransformer and other embedding models
- **Wallet Authentication**: Secure connection using Oracle Wallet

## Installation

### 1. Prerequisites

```bash
pip install oracledb langchain-community langflow sentence-transformers
```

### 2. Component Installation

Place the `oracledb_vectorstore.py` file in your Langflow components directory:

- **Linux/Mac**: `~/.langflow/components/vectorstores/`
- **Windows**: `%USERPROFILE%\.langflow\components\vectorstores\`

Restart Langflow after adding the component.

## Configuration

### Connection Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| **Database User** | Oracle database username | `ADMIN` |
| **Database Password** | Oracle database password | `YourPassword123` |
| **DSN** | Database connection string | `myatp_high` |
| **Wallet Directory** | Path to Oracle wallet directory | `/path/to/wallet` |
| **Wallet Password** | Oracle wallet password | `WalletPass123` |
| **Table Name** | Vector table name | `PDFCOLLECTION` |

### Search Parameters

| Parameter | Description | Default | Advanced |
|-----------|-------------|---------|----------|
| **Number of Results (k)** | Maximum results to return | 5 | No |
| **Search Type** | Search strategy | similarity | Yes |
| **Score Threshold** | Minimum relevance score | 0.35 | Yes |
| **Fetch K** | Candidate pool size | 20 | Yes |
| **MMR Lambda** | Diversity-similarity balance (0-1) | 0.5 | Yes |
| **Distance Strategy** | Distance metric | COSINE | Yes |

## Search Modes

### 1. Similarity Search
Standard vector similarity search using the specified distance metric.

```python
search_type = "similarity"
k = 5
```

### 2. Maximum Marginal Relevance (MMR)
Balances similarity and diversity in results. Useful when you want varied results.

```python
search_type = "mmr"
k = 5
mmr_lambda = 0.5  # 0=max diversity, 1=max similarity
```

### 3. Similarity Score Threshold
Filters results by minimum relevance score. Only returns documents above the threshold.

```python
search_type = "similarity_score_threshold"
score_threshold = 0.35
```

## Distance Strategies

- **COSINE**: Cosine similarity (best for normalized vectors)
- **EUCLIDEAN**: Euclidean distance (L2 distance)
- **DOT_PRODUCT**: Dot product similarity

## Usage Example

### 1. Create Vector Table in Oracle

```sql
CREATE TABLE PDFCOLLECTION (
    id VARCHAR2(100) PRIMARY KEY,
    text CLOB,
    metadata CLOB,
    embedding VECTOR(384)  -- Dimension must match your embedding model
);

CREATE INDEX pdf_vector_idx ON PDFCOLLECTION (embedding)
INDEXTYPE IS VECTOR_INDEX;
```

### 2. Configure in Langflow

1. Add the **Oracle Database Vector Store** component to your flow
2. Connect an embedding model (e.g., SentenceTransformer)
3. Configure connection parameters
4. Set table name and search parameters
5. Add documents or perform searches

### 3. Document Ingestion

```python
# In your Langflow flow, connect:
# Document Loader -> Text Splitter -> Oracle Vector Store (add_documents)
```

### 4. Search

```python
# Configure search query in the component
search_query = "What is machine learning?"
search_type = "similarity"
number_of_results = 5
```

## Important Notes

### Vector Dimensions
The vector dimension in your Oracle table must match your embedding model output:
- **all-MiniLM-L6-v2**: 384 dimensions
- **all-mpnet-base-v2**: 768 dimensions
- **text-embedding-ada-002**: 1536 dimensions

Example:
```sql
CREATE TABLE PDFCOLLECTION (
    embedding VECTOR(384)  -- Match your model
);
```

### Threshold Mode Best Practices
When using `similarity_score_threshold`:
- Set `fetch_k` higher than `k` for optimal filtering
- Experiment with `score_threshold` values (typically 0.2-0.5)
- Lower thresholds = more results, higher thresholds = more selective

### Performance Tips
- Create vector indexes on large tables
- Use appropriate distance strategy for your use case
- Tune `fetch_k` for MMR and threshold modes
- Consider batch size when ingesting documents

## Troubleshooting

### Connection Issues
- Verify wallet files are accessible
- Check DSN configuration in tnsnames.ora
- Ensure wallet password is correct

### Table Not Found
- Verify table name case-sensitivity
- Check table exists in the database
- Ensure user has SELECT/INSERT permissions

### Dimension Mismatch
- Vector dimensions must match embedding model
- Recreate table with correct dimensions if needed

## References

- [Oracle Database 23ai Vector Search](https://docs.oracle.com/en/database/oracle/oracle-database/23/vecse/)
- [LangChain OracleVS](https://python.langchain.com/docs/integrations/vectorstores/oracle)
- [Langflow Documentation](https://docs.langflow.org/)

## License

This component is based on the work by Paul Parkinson and is provided as-is for use with Langflow and Oracle Database.
