#!/usr/bin/env python3
"""
Pinecone Vector Storage - Store documents with embeddings for semantic search

Usage:
    python3 pinecone_store.py --index tax-knowledge --data deductions.json --action create
"""

import json
import os
import argparse
from typing import List, Dict, Any
from datetime import datetime

try:
    from pinecone import Pinecone, ServerlessSpec
except ImportError:
    print("ERROR: pinecone-client not installed. Run: pip install pinecone-client")
    exit(1)

try:
    import openai
except ImportError:
    print("ERROR: openai not installed. Run: pip install openai")
    exit(1)


class PineconeStore:
    """Store and manage vector embeddings in Pinecone"""
    
    def __init__(self, index_name: str, dimension: int = 1536):
        self.index_name = index_name
        self.dimension = dimension
        
        # Initialize Pinecone
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise ValueError("PINECONE_API_KEY environment variable not set")
        
        self.pc = Pinecone(api_key=api_key)
        self.index = None
    
    def create_index(self):
        """Create a new Pinecone index"""
        
        print(f"Creating index: {self.index_name}")
        
        try:
            self.pc.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
            print(f"✅ Index created: {self.index_name}")
        except Exception as e:
            print(f"⚠️  Index may already exist: {e}")
        
        # Connect to index
        self.index = self.pc.Index(self.index_name)
    
    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI"""
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("⚠️  OPENAI_API_KEY not set; using dummy embedding")
            return [0.0] * self.dimension
        
        try:
            client = openai.OpenAI(api_key=api_key)
            response = client.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"ERROR generating embedding: {e}")
            return [0.0] * self.dimension
    
    def store_documents(self, documents: List[Dict[str, Any]], document_type: str = "document"):
        """Store documents with embeddings in Pinecone"""
        
        if not self.index:
            self.index = self.pc.Index(self.index_name)
        
        print(f"Storing {len(documents)} documents of type '{document_type}'...")
        
        vectors_to_upsert = []
        
        for i, doc in enumerate(documents):
            # Create unique ID
            doc_id = f"{document_type}_{i}_{datetime.now().timestamp()}"
            
            # Get text for embedding
            text = doc.get("title", "") + " " + doc.get("description", "")
            if not text.strip():
                text = json.dumps(doc)[:500]
            
            # Generate embedding
            embedding = self.get_embedding(text)
            
            # Prepare metadata
            metadata = {
                "type": document_type,
                "title": doc.get("title", ""),
                "source": doc.get("source", "unknown"),
                "stored_at": datetime.now().isoformat()
            }
            
            vectors_to_upsert.append({
                "id": doc_id,
                "values": embedding,
                "metadata": metadata
            })
            
            if (i + 1) % 10 == 0:
                print(f"  Processed {i + 1}/{len(documents)}")
        
        # Upsert to Pinecone
        try:
            self.index.upsert(vectors=vectors_to_upsert)
            print(f"✅ Stored {len(vectors_to_upsert)} vectors in {self.index_name}")
        except Exception as e:
            print(f"ERROR upserting vectors: {e}")
    
    def load_and_store_json(self, file_path: str, document_type: str = "document"):
        """Load JSON file and store documents"""
        
        print(f"Loading documents from {file_path}...")
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Handle different JSON structures
        documents = []
        if isinstance(data, list):
            documents = data
        elif isinstance(data, dict):
            if "deductions" in data:
                documents = data["deductions"]
            elif "documents" in data:
                documents = data["documents"]
            else:
                documents = [data]
        
        self.store_documents(documents, document_type=document_type)


async def main():
    parser = argparse.ArgumentParser(description="Store documents in Pinecone with embeddings")
    parser.add_argument("--index", required=True, help="Pinecone index name")
    parser.add_argument("--data", help="JSON file with documents to store")
    parser.add_argument("--type", default="document", help="Document type for metadata")
    parser.add_argument("--action", choices=["create", "store", "both"], default="store")
    
    args = parser.parse_args()
    
    store = PineconeStore(index_name=args.index)
    
    if args.action in ["create", "both"]:
        store.create_index()
    
    if args.action in ["store", "both"]:
        if not args.data:
            print("ERROR: --data required for store action")
            exit(1)
        store.load_and_store_json(args.data, document_type=args.type)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
