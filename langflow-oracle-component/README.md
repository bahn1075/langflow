# Oracle Database Vector Store for RAG Applications

A custom Langflow component that integrates **Oracle 23ai Vector Store** with local embeddings for building RAG (Retrieval Augmented Generation) applications. This component provides configurable retrieval options and supports multiple distance metrics for semantic search.

## Features

- **Native Oracle 23ai Vector Support**: Leverage Oracle Database's built-in vector capabilities
- **Local Embeddings**: Use SentenceTransformers or other local embedding models (no cloud dependencies)
- **Multiple Search Modes**:
  - Standard similarity search
  - MMR (Maximum Marginal Relevance) for diverse results
  - Similarity score threshold filtering
- **Flexible Distance Metrics**: COSINE, EUCLIDEAN, DOT_PRODUCT
- **Secure Authentication**: Oracle Wallet-based connection
- **Langflow Integration**: Drop-in component for visual AI workflows
- **Standalone Usage**: Can be used independently in Python applications

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Database Setup](#database-setup)
- [Component Configuration](#component-configuration)
- [Usage Examples](#usage-examples)
- [Architecture](#architecture)
- [Directory Structure](#directory-structure)
- [Troubleshooting](#troubleshooting)
- [Performance Optimization](#performance-optimization)
- [Contributing](#contributing)

## Installation

### Prerequisites

- Python 3.8+
- Oracle Database 23ai with Vector capabilities
- Oracle Wallet for secure authentication
- Langflow (for UI integration)

### Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `oracledb>=2.0.0`
- `langchain>=0.1.0`
- `langchain-community>=0.0.20`
- `langflow>=1.0.0`
- `sentence-transformers>=2.2.0`

### Install Component in Langflow

#### Linux/Mac:
```bash
mkdir -p ~/.langflow/components/vectorstores
cp components/vectorstores/oracledb_vectorstore.py ~/.langflow/components/vectorstores/
```

#### Windows:
```powershell
mkdir $env:USERPROFILE\.langflow\components\vectorstores
copy components\vectorstores\oracledb_vectorstore.py $env:USERPROFILE\.langflow\components\vectorstores\
```

Restart Langflow after installation.

## Quick Start

### 1. Create Vector Table in Oracle

```sql
-- For 384-dimension embeddings (all-MiniLM-L6-v2)
CREATE TABLE PDFCOLLECTION (
    id VARCHAR2(100) PRIMARY KEY,
    text CLOB,
    metadata CLOB,
    embedding VECTOR(384),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 1. 기본 벡터 인덱스 (HNSW)
CREATE VECTOR INDEX pdf_vector_idx ON PDFCOLLECTION (embedding)
ORGANIZATION NEIGHBOR PARTITIONS
WITH DISTANCE COSINE;

-- 또는

-- 2. IVF (Inverted File) 인덱스 (대용량 데이터에 적합)
CREATE VECTOR INDEX pdf_vector_idx ON PDFCOLLECTION (embedding)
ORGANIZATION INVERTED FILE FLAT
WITH DISTANCE COSINE
WITH TARGET ACCURACY 95;

-- 또는

-- 3. 인메모리 벡터 인덱스 (가장 빠름, 메모리 충분할 때)
CREATE VECTOR INDEX pdf_vector_idx ON PDFCOLLECTION (embedding)
ORGANIZATION INMEMORY NEIGHBOR GRAPH
WITH DISTANCE COSINE
WITH TARGET ACCURACY 95;
```

See [sql/](sql/) directory for more table creation scripts.

### 2. Configure Environment

Copy `.env.example` to `.env` and update with your credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```env
ORACLE_DB_USER=ADMIN
ORACLE_DB_PASSWORD=YourPassword
ORACLE_DSN=myatp_high
ORACLE_WALLET_DIR=/path/to/wallet
ORACLE_WALLET_PASSWORD=YourWalletPassword
```

### 3. Use in Langflow

1. Open Langflow UI
2. Find "Oracle Database Vector Store" in Vector Stores section
3. Configure connection parameters
4. Connect an embedding model
5. Add documents or perform searches

### 4. Use in Python (Standalone)

```python
from components.vectorstores.oracledb_vectorstore import OracleDatabaseVectorStoreComponent
from langchain_community.embeddings import HuggingFaceEmbeddings

# Initialize embedding model
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Configure vector store
vector_store = OracleDatabaseVectorStoreComponent(
    db_user="ADMIN",
    db_password="YourPassword",
    dsn="myatp_high",
    wallet_dir="/path/to/wallet",
    wallet_password="WalletPassword",
    table_name="PDFCOLLECTION",
    embedding=embeddings
)

# Add documents
from langchain.schema import Document
docs = [
    Document(page_content="Your text here", metadata={"source": "doc.pdf"})
]
vector_store.add_documents(docs)

# Search
results = vector_store.search_documents()
```

See [examples/](examples/) for more detailed examples.

## Database Setup

### Supported Vector Dimensions

Match the vector dimension with your embedding model:

| Embedding Model | Dimensions | SQL File |
|----------------|------------|----------|
| all-MiniLM-L6-v2 | 384 | [create_vector_table.sql](sql/create_vector_table.sql) |
| all-mpnet-base-v2 | 768 | [create_vector_table_768.sql](sql/create_vector_table_768.sql) |
| text-embedding-ada-002 | 1536 | [create_vector_table_1536.sql](sql/create_vector_table_1536.sql) |

### Oracle Wallet Setup

1. Download wallet from Oracle Cloud Console
2. Extract to a secure directory
3. Update `tnsnames.ora` and `sqlnet.ora` if needed
4. Note the wallet directory path for configuration

### Verify Setup

```sql
-- Check table structure
DESC PDFCOLLECTION;

-- Verify index
SELECT index_name, status FROM user_indexes
WHERE table_name = 'PDFCOLLECTION';

-- Test connection
SELECT COUNT(*) FROM PDFCOLLECTION;
```

## Component Configuration

### Connection Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Database User | SecretStr | Yes | Oracle username (e.g., ADMIN) |
| Database Password | SecretStr | Yes | Oracle password |
| DSN | SecretStr | Yes | Database connection string |
| Wallet Directory | SecretStr | Yes | Path to Oracle wallet |
| Wallet Password | SecretStr | Yes | Wallet password |
| Table Name | String | Yes | Vector table name |

### Search Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| Number of Results (k) | Integer | 5 | Max results to return |
| Search Type | Dropdown | similarity | Search strategy |
| Score Threshold | Float | 0.35 | Min relevance score |
| Fetch K | Integer | 20 | Candidate pool size |
| MMR Lambda | Float | 0.5 | Diversity balance (0-1) |
| Distance Strategy | Dropdown | COSINE | Distance metric |

### Search Types

1. **similarity**: Standard vector similarity search
2. **mmr**: Maximum Marginal Relevance (diverse results)
3. **similarity_score_threshold**: Threshold-based filtering

### Distance Strategies

- **COSINE**: Best for normalized embeddings (recommended)
- **EUCLIDEAN**: L2 distance
- **DOT_PRODUCT**: For unnormalized vectors

## Usage Examples

### Example 1: PDF Question Answering

```python
# See examples/standalone_usage.py for complete code

# 1. Load and split PDF
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

loader = PyPDFLoader("document.pdf")
documents = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
chunks = splitter.split_documents(documents)

# 2. Add to vector store
vector_store.add_documents(chunks)

# 3. Search
query = "What is the main topic?"
results = vector_store.similarity_search(query, k=5)
```

### Example 2: MMR Search for Diversity

```python
# Get diverse results
results = vector_store.max_marginal_relevance_search(
    query="machine learning",
    k=5,
    fetch_k=20,
    lambda_mult=0.5  # Balance similarity and diversity
)
```

### Example 3: Filtered Search

```python
# Search with metadata filter
results = vector_store.similarity_search(
    query="database",
    k=5,
    filter={"source": "specific_doc.pdf"}
)
```

See [examples/](examples/) directory for more comprehensive examples.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Langflow UI                          │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│      Oracle Vector Store Component                      │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Connection Manager (Wallet Auth)                │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Embedding Integration                           │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Search Engine (Similarity/MMR/Threshold)        │   │
│  └─────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              Oracle 23ai Database                        │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Vector Tables (PDFCOLLECTION)                   │   │
│  │  - id, text, metadata, embedding                 │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Vector Index (Fast Similarity Search)           │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Directory Structure

```
.
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment configuration template
├── components/                        # Langflow components
│   ├── __init__.py
│   └── vectorstores/
│       ├── __init__.py
│       ├── oracledb_vectorstore.py   # Main component
│       └── README_oracle_vectorstore.md
├── sql/                               # SQL scripts
│   ├── create_vector_table.sql       # 384 dimensions
│   ├── create_vector_table_768.sql   # 768 dimensions
│   ├── create_vector_table_1536.sql  # 1536 dimensions
│   └── query_examples.sql            # Sample queries
└── examples/                          # Usage examples
    ├── standalone_usage.py            # Python examples
    └── langflow_integration.md        # Langflow guide
```

## Troubleshooting

### Connection Issues

**Problem**: Cannot connect to Oracle Database

**Solutions**:
1. Verify wallet files are in correct directory
2. Check DSN in `tnsnames.ora`
3. Ensure wallet password is correct
4. Test with SQL Developer first

### Dimension Mismatch

**Problem**: Error about vector dimension mismatch

**Solution**:
```sql
-- Check current dimension
DESC PDFCOLLECTION;

-- Drop and recreate with correct dimension
DROP TABLE PDFCOLLECTION;
CREATE TABLE PDFCOLLECTION (
    embedding VECTOR(384)  -- Match your embedding model
);
```

### No Results Returned

**Problem**: Search returns empty results

**Solutions**:
1. Check if documents exist: `SELECT COUNT(*) FROM PDFCOLLECTION;`
2. Lower score threshold if using threshold mode
3. Verify embedding model is consistent between ingestion and search
4. Check metadata filters

### Component Not Loading in Langflow

**Solutions**:
1. Verify file location: `~/.langflow/components/vectorstores/`
2. Check file permissions
3. Review Langflow logs for import errors
4. Restart Langflow completely

## Performance Optimization

### 1. Create Vector Index

Always create a vector index for production use:

```sql
CREATE INDEX pdf_vector_idx ON PDFCOLLECTION (embedding)
INDEXTYPE IS VECTOR_INDEX;
```

### 2. Batch Document Insertion

Insert documents in batches rather than one at a time:

```python
# Good: Batch insert
vector_store.add_documents(large_document_list)

# Bad: Individual inserts
for doc in large_document_list:
    vector_store.add_documents([doc])
```

### 3. Tune Search Parameters

- Set `fetch_k` higher than `k` for MMR/threshold searches
- Experiment with different `score_threshold` values
- Use appropriate distance strategy for your embeddings

### 4. Monitor Table Size

```sql
SELECT ROUND(SUM(bytes)/1024/1024, 2) as size_mb
FROM user_segments
WHERE segment_name = 'PDFCOLLECTION';
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

Based on the work by Paul Parkinson. This project is provided as-is for use with Langflow and Oracle Database.

## References

- [Oracle Database 23ai Vector Search Documentation](https://docs.oracle.com/en/database/oracle/oracle-database/23/vecse/)
- [LangChain OracleVS Integration](https://python.langchain.com/docs/integrations/vectorstores/oracle)
- [Langflow Documentation](https://docs.langflow.org/)
- [Original Repository](https://github.com/paulparkinson/langflow-agenticai-oracle-mcp-vector-nl2sql)

## Support

For issues and questions:
- Check the [Troubleshooting](#troubleshooting) section
- Review [examples/](examples/) directory
- Consult Oracle Database documentation
- Check Langflow community resources

---

**Note**: This component requires Oracle Database 23ai or later with vector support enabled.
