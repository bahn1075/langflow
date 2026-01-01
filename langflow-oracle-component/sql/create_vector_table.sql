-- Oracle Database 23ai Vector Store Table Creation
-- This script creates a table for storing document embeddings

-- ============================================
-- Create Vector Table
-- ============================================

-- Drop table if exists (use with caution in production)
-- DROP TABLE PDFCOLLECTION CASCADE CONSTRAINTS;

-- Create table with vector column
-- Adjust the vector dimension based on your embedding model:
--   - all-MiniLM-L6-v2: 384 dimensions
--   - all-mpnet-base-v2: 768 dimensions
--   - text-embedding-ada-002 (OpenAI): 1536 dimensions
--   - text-embedding-3-small (OpenAI): 1536 dimensions
--   - text-embedding-3-large (OpenAI): 3072 dimensions

CREATE TABLE PDFCOLLECTION (
    id VARCHAR2(100) PRIMARY KEY,
    text CLOB,
    metadata CLOB,
    embedding VECTOR(384),  -- Change dimension to match your model
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Create Vector Index for Performance
-- ============================================

-- Create a vector index for efficient similarity search
-- This dramatically improves query performance on large datasets

CREATE INDEX pdf_vector_idx ON PDFCOLLECTION (embedding)
INDEXTYPE IS VECTOR_INDEX;

-- ============================================
-- Optional: Grant Permissions
-- ============================================

-- If you need to grant access to other users
-- GRANT SELECT, INSERT, UPDATE, DELETE ON PDFCOLLECTION TO <username>;

-- ============================================
-- Verify Table Creation
-- ============================================

-- Check table structure
DESC PDFCOLLECTION;

-- Check if index was created
SELECT index_name, index_type, table_name
FROM user_indexes
WHERE table_name = 'PDFCOLLECTION';

-- ============================================
-- Sample Data Insert (Optional)
-- ============================================

-- Example: Insert a sample vector (all zeros for demonstration)
/*
DECLARE
    v_vector VECTOR(384);
BEGIN
    v_vector := VECTOR('[' || RPAD('0,', 384*2, '0,') || '0]', 384, FLOAT32);

    INSERT INTO PDFCOLLECTION (id, text, metadata, embedding)
    VALUES (
        'sample-1',
        'This is a sample document for testing.',
        '{"source": "sample", "page": 1}',
        v_vector
    );

    COMMIT;
END;
/
*/

-- ============================================
-- Clean Up (Use with caution)
-- ============================================

-- To start fresh (WARNING: This deletes all data)
-- TRUNCATE TABLE PDFCOLLECTION;

-- To drop the table completely
-- DROP TABLE PDFCOLLECTION CASCADE CONSTRAINTS;
