-- Oracle Database 23ai Vector Store Table Creation
-- For 768-dimension embeddings (e.g., all-mpnet-base-v2)

CREATE TABLE PDFCOLLECTION (
    id VARCHAR2(100) PRIMARY KEY,
    text CLOB,
    metadata CLOB,
    embedding VECTOR(768),  -- 768 dimensions
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create vector index
CREATE INDEX pdf_vector_idx ON PDFCOLLECTION (embedding)
INDEXTYPE IS VECTOR_INDEX;

-- Verify
DESC PDFCOLLECTION;
