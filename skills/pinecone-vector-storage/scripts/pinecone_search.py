#!/usr/bin/env python3
"""
Pinecone Vector Search - Semantic search across stored documents

Usage:
    python3 pinecone_search.py --index tax-knowledge --query "home office deduction"
"""

import os
import argparse
import json
from typing import List, Dict, Any

try:
    from pinecone import Pinecone
except ImportError:
    print("ERROR: pinecone-client not installed. Run: pip install pinecone-client")
    exit(1)

try:
    import openai
except ImportError:
    print("ERROR: openai not installed. Run: pip install openai")
    exit(1)


class PineconeSearch:
    """Search vector embeddings in Pinecone"""
    
    def __init__(self, index_name: str):
        self.index_name = index_name
        
        # Initialize Pinecone
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise ValueError("PINECONE_API_KEY environment variable not set")
        
        self.pc = Pinecone(api_key=api_key)
        self.index = self.pc.Index(index_name)
    
    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for query text"""
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("⚠️  OPENAI_API_KEY not set; using dummy embedding")
            return [0.0] * 1536
        
        try:
            client = openai.OpenAI(api_key=api_key)
            response = client.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"ERROR generating embedding: {e}")
            return [0.0] * 1536
    
    def search(self, query: str, top_k: int = 5, document_type: str = None) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        
        print(f"Searching for: '{query}'")
        
        # Get embedding for query
        query_embedding = self.get_embedding(query)
        
        # Build filter if document_type specified
        filter_dict = None
        if document_type:
            filter_dict = {"type": {"$eq": document_type}}
        
        # Search in Pinecone
        try:
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict
            )
            
            # Format results
            formatted_results = []
            for match in results.get("matches", []):
                formatted_results.append({
                    "id": match["id"],
                    "score": match["score"],
                    "metadata": match.get("metadata", {})
                })
            
            return formatted_results
        
        except Exception as e:
            print(f"ERROR searching index: {e}")
            return []
    
    def search_deductions(self, situation: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Search deductions relevant to user situation"""
        
        return self.search(
            query=situation,
            top_k=top_k,
            document_type="deduction"
        )
    
    def find_similar(self, query: str, document_type: str = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """Alias for search"""
        return self.search(query=query, top_k=top_k, document_type=document_type)


def main():
    parser = argparse.ArgumentParser(description="Semantic search in Pinecone")
    parser.add_argument("--index", required=True, help="Pinecone index name")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--type", help="Filter by document type (deduction, credit, etc.)")
    parser.add_argument("--top-k", type=int, default=5, help="Number of results to return")
    parser.add_argument("--output", help="Save results to JSON file")
    
    args = parser.parse_args()
    
    search = PineconeSearch(index_name=args.index)
    results = search.search(
        query=args.query,
        top_k=args.top_k,
        document_type=args.type
    )
    
    print(f"\n✅ Found {len(results)} results:\n")
    
    for i, result in enumerate(results, 1):
        metadata = result.get("metadata", {})
        print(f"{i}. {metadata.get('title', 'Untitled')} (score: {result['score']:.3f})")
        print(f"   Type: {metadata.get('type', 'unknown')}")
        print(f"   Source: {metadata.get('source', 'unknown')}\n")
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {args.output}")


if __name__ == "__main__":
    main()
