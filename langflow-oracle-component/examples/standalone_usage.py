"""
Standalone Usage Example for Oracle Vector Store Component

This example demonstrates how to use the Oracle Vector Store component
outside of Langflow for direct Python integration.
"""

import oracledb
from typing import List
from langchain_community.vectorstores.oraclevs import OracleVS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

# ============================================
# Configuration
# ============================================

# Oracle Database Configuration
DB_CONFIG = {
    "user": "ADMIN",
    "password": "YourPassword123",
    "dsn": "myatp_high",
    "config_dir": "/path/to/wallet",
    "wallet_location": "/path/to/wallet",
    "wallet_password": "WalletPassword123",
}

TABLE_NAME = "PDFCOLLECTION"

# ============================================
# Initialize Embedding Model
# ============================================

def get_embedding_model():
    """Initialize local embedding model."""
    # Using HuggingFace SentenceTransformers (384 dimensions)
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    return embeddings

# ============================================
# Create Oracle Connection
# ============================================

def create_connection():
    """Create Oracle database connection."""
    try:
        conn = oracledb.connect(**DB_CONFIG)
        print("✅ Connected to Oracle Database")
        return conn
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        raise

# ============================================
# Initialize Vector Store
# ============================================

def initialize_vector_store(conn, embeddings):
    """Initialize Oracle Vector Store."""
    vector_store = OracleVS(
        client=conn,
        table_name=TABLE_NAME,
        distance_strategy=DistanceStrategy.COSINE,
        embedding_function=embeddings
    )
    print(f"✅ Vector store initialized with table: {TABLE_NAME}")
    return vector_store

# ============================================
# Add Documents
# ============================================

def add_documents_example(vector_store):
    """Add sample documents to the vector store."""
    documents = [
        Document(
            page_content="Oracle Database 23ai introduces native vector support for AI applications.",
            metadata={"source": "oracle_docs.pdf", "page": 1, "category": "database"}
        ),
        Document(
            page_content="RAG (Retrieval Augmented Generation) combines vector search with LLMs.",
            metadata={"source": "rag_guide.pdf", "page": 5, "category": "ai"}
        ),
        Document(
            page_content="Vector embeddings represent text as numerical vectors in high-dimensional space.",
            metadata={"source": "ml_fundamentals.pdf", "page": 12, "category": "machine_learning"}
        ),
        Document(
            page_content="Cosine similarity measures the angle between two vectors.",
            metadata={"source": "vector_math.pdf", "page": 3, "category": "mathematics"}
        ),
    ]

    print(f"\n📝 Adding {len(documents)} documents...")
    vector_store.add_documents(documents)
    print(f"✅ Successfully added {len(documents)} documents")

# ============================================
# Similarity Search
# ============================================

def similarity_search_example(vector_store):
    """Perform similarity search."""
    query = "What is vector database?"
    k = 3

    print(f"\n🔍 Searching for: '{query}'")
    results = vector_store.similarity_search(query, k=k)

    print(f"\n📊 Top {k} Results:")
    for i, doc in enumerate(results, 1):
        print(f"\n{i}. {doc.page_content}")
        print(f"   Metadata: {doc.metadata}")

# ============================================
# Similarity Search with Scores
# ============================================

def similarity_search_with_score_example(vector_store):
    """Perform similarity search with relevance scores."""
    query = "How does RAG work?"
    k = 3

    print(f"\n🔍 Searching with scores for: '{query}'")
    results = vector_store.similarity_search_with_score(query, k=k)

    print(f"\n📊 Top {k} Results with Scores:")
    for i, (doc, score) in enumerate(results, 1):
        print(f"\n{i}. Score: {score:.4f}")
        print(f"   Content: {doc.page_content}")
        print(f"   Metadata: {doc.metadata}")

# ============================================
# MMR Search
# ============================================

def mmr_search_example(vector_store):
    """Perform Maximum Marginal Relevance search for diverse results."""
    query = "vector embeddings"
    k = 3
    fetch_k = 10
    lambda_mult = 0.5  # Balance between similarity (1.0) and diversity (0.0)

    print(f"\n🔍 MMR Search for: '{query}' (lambda={lambda_mult})")
    results = vector_store.max_marginal_relevance_search(
        query=query,
        k=k,
        fetch_k=fetch_k,
        lambda_mult=lambda_mult
    )

    print(f"\n📊 Top {k} Diverse Results:")
    for i, doc in enumerate(results, 1):
        print(f"\n{i}. {doc.page_content}")
        print(f"   Metadata: {doc.metadata}")

# ============================================
# Search with Metadata Filter
# ============================================

def search_with_filter_example(vector_store):
    """Search with metadata filtering."""
    query = "database"
    filter_dict = {"category": "database"}

    print(f"\n🔍 Filtered search for: '{query}' with filter {filter_dict}")
    results = vector_store.similarity_search(
        query=query,
        k=5,
        filter=filter_dict
    )

    print(f"\n📊 Filtered Results:")
    for i, doc in enumerate(results, 1):
        print(f"\n{i}. {doc.page_content}")
        print(f"   Metadata: {doc.metadata}")

# ============================================
# As Retriever
# ============================================

def retriever_example(vector_store):
    """Use vector store as a retriever."""
    # Create retriever with score threshold
    retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            "k": 5,
            "score_threshold": 0.3
        }
    )

    query = "What are vectors?"
    print(f"\n🔍 Retriever search for: '{query}'")
    results = retriever.get_relevant_documents(query)

    print(f"\n📊 Retrieved {len(results)} documents:")
    for i, doc in enumerate(results, 1):
        print(f"\n{i}. {doc.page_content}")

# ============================================
# Main Execution
# ============================================

def main():
    """Main execution function."""
    print("=" * 60)
    print("Oracle Vector Store - Standalone Usage Example")
    print("=" * 60)

    # Initialize
    embeddings = get_embedding_model()
    conn = create_connection()
    vector_store = initialize_vector_store(conn, embeddings)

    # Add documents (comment out if already populated)
    add_documents_example(vector_store)

    # Run search examples
    similarity_search_example(vector_store)
    similarity_search_with_score_example(vector_store)
    mmr_search_example(vector_store)
    search_with_filter_example(vector_store)
    retriever_example(vector_store)

    # Close connection
    conn.close()
    print("\n✅ Connection closed")
    print("=" * 60)

if __name__ == "__main__":
    main()
