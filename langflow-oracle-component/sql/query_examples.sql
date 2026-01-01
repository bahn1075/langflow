-- Oracle Vector Store Query Examples
-- Examples of how to query and manage your vector store

-- ============================================
-- Basic Queries
-- ============================================

-- Count total documents
SELECT COUNT(*) as total_documents FROM PDFCOLLECTION;

-- View all document metadata
SELECT id,
       SUBSTR(text, 1, 100) as text_preview,
       metadata,
       created_at
FROM PDFCOLLECTION
ORDER BY created_at DESC;

-- ============================================
-- Vector Search Examples
-- ============================================

-- Note: Vector similarity searches are typically performed through
-- the Langflow component or Python API, not raw SQL.
-- However, here are some raw SQL examples:

-- Example: Find similar vectors using cosine similarity
-- (Replace the embedding vector with your actual query vector)
/*
SELECT id,
       text,
       VECTOR_DISTANCE(
           embedding,
           TO_VECTOR('[0.1, 0.2, ...]', 384, FLOAT32),
           COSINE
       ) as distance
FROM PDFCOLLECTION
ORDER BY distance
FETCH FIRST 5 ROWS ONLY;
*/

-- ============================================
-- Metadata Filtering
-- ============================================

-- Search by metadata (JSON_VALUE for JSON metadata)
SELECT id, text, metadata
FROM PDFCOLLECTION
WHERE JSON_VALUE(metadata, '$.source') = 'specific_document.pdf';

-- Find documents by date range
SELECT id, text, created_at
FROM PDFCOLLECTION
WHERE created_at > SYSDATE - 7
ORDER BY created_at DESC;

-- ============================================
-- Maintenance Queries
-- ============================================

-- Check table size
SELECT
    ROUND(SUM(bytes)/1024/1024, 2) as size_mb
FROM user_segments
WHERE segment_name = 'PDFCOLLECTION';

-- Check index status
SELECT index_name, status, tablespace_name
FROM user_indexes
WHERE table_name = 'PDFCOLLECTION';

-- Rebuild index if needed
-- ALTER INDEX pdf_vector_idx REBUILD;

-- ============================================
-- Data Management
-- ============================================

-- Delete old documents (older than 30 days)
-- DELETE FROM PDFCOLLECTION WHERE created_at < SYSDATE - 30;

-- Delete specific document
-- DELETE FROM PDFCOLLECTION WHERE id = 'document-id-here';

-- Update document metadata
/*
UPDATE PDFCOLLECTION
SET metadata = '{"source": "updated_source.pdf", "page": 1}'
WHERE id = 'document-id-here';
*/

-- ============================================
-- Statistics
-- ============================================

-- Group by metadata source
SELECT
    JSON_VALUE(metadata, '$.source') as source,
    COUNT(*) as document_count
FROM PDFCOLLECTION
GROUP BY JSON_VALUE(metadata, '$.source')
ORDER BY document_count DESC;

-- ============================================
-- Export/Backup
-- ============================================

-- Export table structure
-- SQL Developer: Right-click table > Export

-- Create backup table
-- CREATE TABLE PDFCOLLECTION_BACKUP AS SELECT * FROM PDFCOLLECTION;
