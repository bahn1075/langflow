# Langflow Integration Guide

This guide explains how to use the Oracle Vector Store component within Langflow.

## Setup Steps

### 1. Install the Component

Copy the component file to your Langflow components directory:

**Linux/Mac:**
```bash
mkdir -p ~/.langflow/components/vectorstores
cp components/vectorstores/oracledb_vectorstore.py ~/.langflow/components/vectorstores/
```

**Windows:**
```powershell
mkdir $env:USERPROFILE\.langflow\components\vectorstores
copy components\vectorstores\oracledb_vectorstore.py $env:USERPROFILE\.langflow\components\vectorstores\
```

### 2. Restart Langflow

```bash
langflow run
```

The Oracle Database Vector Store component should now appear in the Vector Stores section.

## Basic RAG Flow

### Flow Architecture

```
┌─────────────────┐
│  Document       │
│  Loader (PDF)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Text Splitter  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│  Embedding      │◄─────┤  Oracle Vector   │
│  Model          │      │  Store           │
└─────────────────┘      └────────┬─────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │  Search Query   │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │  LLM (GPT/      │
                         │  Claude/etc)    │
                         └─────────────────┘
```

### Component Configuration in Langflow

#### 1. Document Ingestion Flow

**Components:**
1. **File Upload / PDF Loader**
   - Upload your PDF documents

2. **Text Splitter**
   - Type: RecursiveCharacterTextSplitter
   - Chunk Size: 1000
   - Chunk Overlap: 200

3. **Embedding Model**
   - Type: HuggingFace Embeddings
   - Model: sentence-transformers/all-MiniLM-L6-v2

4. **Oracle Vector Store**
   - Connect embedding model
   - Configure database credentials
   - Set table name: PDFCOLLECTION
   - Action: Add Documents

**Flow Connections:**
```
File Upload → Text Splitter → Oracle Vector Store (with Embedding)
```

#### 2. Query/Search Flow

**Components:**
1. **Oracle Vector Store**
   - Configure same settings as above
   - Set Search Query input
   - Number of Results: 5
   - Search Type: similarity

2. **Prompt Template**
   ```
   Context: {context}

   Question: {question}

   Answer the question based only on the provided context.
   ```

3. **LLM (OpenAI/Anthropic/etc)**
   - Model: gpt-4 or claude-3

**Flow Connections:**
```
User Query → Oracle Vector Store → Prompt Template → LLM → Output
```

## Advanced Configurations

### MMR Search for Diverse Results

In the Oracle Vector Store component:
- Search Type: `mmr`
- MMR Lambda: `0.5` (adjust between 0-1)
- Fetch K: `20`
- Number of Results: `5`

### Score Threshold Filtering

For quality-focused results:
- Search Type: `similarity_score_threshold`
- Score Threshold: `0.35` (adjust based on your needs)
- Fetch K: `20`

### Distance Strategies

Choose based on your embedding model:
- **COSINE**: Best for normalized embeddings (recommended)
- **EUCLIDEAN**: L2 distance
- **DOT_PRODUCT**: For unnormalized vectors

## Example Flows

### 1. PDF Q&A System

```json
{
  "name": "PDF Q&A with Oracle Vector Store",
  "components": [
    {
      "type": "PDFLoader",
      "config": { "file_path": "document.pdf" }
    },
    {
      "type": "RecursiveCharacterTextSplitter",
      "config": { "chunk_size": 1000, "chunk_overlap": 200 }
    },
    {
      "type": "HuggingFaceEmbeddings",
      "config": { "model_name": "all-MiniLM-L6-v2" }
    },
    {
      "type": "OracleDatabaseVectorStore",
      "config": {
        "db_user": "ADMIN",
        "table_name": "PDFCOLLECTION",
        "search_type": "similarity",
        "number_of_results": 5
      }
    }
  ]
}
```

### 2. Multi-Document Search

Configure multiple document loaders feeding into the same Oracle Vector Store to create a unified knowledge base.

### 3. Conversational RAG

Add a Conversation Buffer Memory component to maintain chat history while querying the vector store.

## Troubleshooting

### Component Not Appearing

1. Verify file location: `~/.langflow/components/vectorstores/oracledb_vectorstore.py`
2. Check file permissions
3. Restart Langflow completely
4. Check Langflow logs for import errors

### Connection Errors

1. Verify Oracle wallet path
2. Check DSN configuration
3. Test connection with SQL Developer first
4. Ensure firewall allows connection

### Dimension Mismatch

Ensure your Oracle table vector dimension matches your embedding model:
```sql
-- Check current dimension
DESC PDFCOLLECTION;

-- Recreate table with correct dimension if needed
DROP TABLE PDFCOLLECTION;
CREATE TABLE PDFCOLLECTION (
    id VARCHAR2(100) PRIMARY KEY,
    text CLOB,
    metadata CLOB,
    embedding VECTOR(384)  -- Match your model
);
```

### No Results Returned

1. Check if documents are actually in the table:
   ```sql
   SELECT COUNT(*) FROM PDFCOLLECTION;
   ```
2. Lower the score threshold if using threshold mode
3. Verify embedding model is the same for ingestion and search

## Performance Tips

1. **Index Creation**: Always create vector index for large datasets
2. **Batch Ingestion**: Process documents in batches
3. **Fetch K Tuning**: Set fetch_k higher than k for better MMR/threshold results
4. **Connection Pooling**: Reuse connections when possible

## Best Practices

1. **Consistent Embeddings**: Always use the same embedding model for ingestion and search
2. **Metadata**: Add rich metadata for filtering capabilities
3. **Chunk Size**: Experiment with different chunk sizes (500-1500 tokens)
4. **Regular Maintenance**: Monitor table size and rebuild indexes periodically

## Resources

- [Langflow Documentation](https://docs.langflow.org/)
- [Oracle Vector Search Guide](https://docs.oracle.com/en/database/oracle/oracle-database/23/vecse/)
- [LangChain Documentation](https://python.langchain.com/)
