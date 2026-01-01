-- Oracle Database 23ai Vector Store Table Creation
-- For 1536-dimension embeddings (e.g., OpenAI text-embedding-ada-002)

CREATE TABLE PDFCOLLECTION (
    id VARCHAR2(100) PRIMARY KEY,
    text CLOB,
    metadata CLOB,
    embedding VECTOR(1536),  -- 1536 dimensions
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create vector index
CREATE INDEX pdf_vector_idx ON PDFCOLLECTION (embedding)
INDEXTYPE IS VECTOR_INDEX;

-- Verify
DESC PDFCOLLECTION;
