#!/usr/bin/env python3
"""
Basic RAG Implementation Example
Demonstrates the three-step RAG process: Retrieval → Augmentation → Generation
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.rag_orchestrator import RAGOrchestrator
import time

def main():
    """Demonstrate the basic RAG implementation"""
    print("🔍 Basic RAG Implementation Example")
    print("=" * 60)
    print("This example shows the three-step RAG process:")
    print("1. Retrieval: Find relevant documents")
    print("2. Augmentation: Build context from documents")
    print("3. Generation: Generate answer using GPT-4")
    print("=" * 60)
    
    # Initialize RAG orchestrator
    print("\n🚀 Initializing RAG Orchestrator...")
    try:
        rag = RAGOrchestrator()
        print("✅ RAG Orchestrator initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize RAG: {e}")
        print("Make sure your .env file is configured correctly.")
        return
    
    # Validate pipeline
    print("\n🔧 Validating RAG Pipeline...")
    validation = rag.validate_pipeline()
    print(f"Pipeline Status: {validation.get('overall', 'unknown')}")
    
    for component, status in validation.items():
        if component != 'overall':
            print(f"  {component.capitalize()}: {status.get('status', 'unknown')}")
    
    if validation.get('overall') != 'healthy':
        print("⚠️  Some components may not be working correctly.")
    
    # Example 1: Search Only (Step 1: Retrieval)
    print("\n" + "="*60)
    print("Example 1: Search Only (Step 1: Retrieval)")
    print("="*60)
    
    search_query = "machine learning algorithms"
    print(f"Searching for: '{search_query}'")
    
    search_results = rag.search_only(search_query, top_k=3, search_type="hybrid")
    
    if search_results:
        print(f"✅ Found {len(search_results)} relevant documents:")
        for i, result in enumerate(search_results, 1):
            print(f"\n  Document {i}:")
            print(f"    File: {result['filename']}")
            print(f"    Page: {result['page_number']}")
            print(f"    Score: {result['score']:.3f}")
            print(f"    Content: {result['content'][:100]}...")
    else:
        print("❌ No documents found. Make sure you have uploaded documents first.")
    
    # Example 2: Complete RAG Pipeline
    print("\n" + "="*60)
    print("Example 2: Complete RAG Pipeline")
    print("="*60)
    print("This demonstrates all three steps working together:")
    
    question = "What are the main types of machine learning?"
    print(f"\nQuestion: {question}")
    print("\nProcessing steps:")
    print("  1. 🔍 Retrieval: Searching for relevant documents...")
    print("  2. 🔧 Augmentation: Building context from documents...")
    print("  3. 🤖 Generation: Generating answer with GPT-4...")
    
    # Run complete RAG pipeline
    start_time = time.time()
    result = rag.ask(
        question=question,
        top_k=5,
        search_type="hybrid",
        context_length=4000,
        temperature=0.7,
        max_tokens=500
    )
    total_time = time.time() - start_time
    
    # Display results
    print(f"\n✅ RAG Pipeline completed in {total_time:.2f} seconds!")
    print(f"\n🤖 Answer:")
    print(f"   {result['answer']}")
    
    print(f"\n📊 Metrics:")
    print(f"   Confidence: {result['confidence']:.2f}")
    print(f"   Processing Time: {result['processing_time']:.2f}s")
    print(f"   Context Length: {result['context_length']:,} characters")
    print(f"   Sources Used: {len(result['sources'])}")
    
    if result['sources']:
        print(f"\n📚 Sources:")
        for i, source in enumerate(result['sources'], 1):
            print(f"   {i}. {source['filename']} (Page {source['page']})")
            print(f"      Score: {source['score']:.3f}")
    
    # Example 3: Step-by-step breakdown
    print("\n" + "="*60)
    print("Example 3: Step-by-Step Breakdown")
    print("="*60)
    
    question2 = "What is deep learning?"
    print(f"\nQuestion: {question2}")
    
    # Step 1: Retrieval
    print("\nStep 1: 🔍 Retrieval")
    retrieved_chunks = rag.search_only(question2, top_k=3)
    print(f"   Retrieved {len(retrieved_chunks)} documents")
    
    if retrieved_chunks:
        # Step 2: Augmentation
        print("\nStep 2: 🔧 Augmentation")
        from core.augmentation import AugmentationComponent
        augmentation = AugmentationComponent()
        context = augmentation.augment(retrieved_chunks, max_length=2000)
        print(f"   Built context with {len(context)} characters")
        
        # Step 3: Generation
        print("\nStep 3: 🤖 Generation")
        from core.generation import GenerationComponent
        generation = GenerationComponent()
        answer_result = generation.generate(question2, context, temperature=0.7, max_tokens=300)
        print(f"   Generated answer: {answer_result['answer'][:100]}...")
        print(f"   Confidence: {answer_result['confidence']:.2f}")
        print(f"   Tokens used: {answer_result['tokens_used']}")
    
    # Example 4: Different search types
    print("\n" + "="*60)
    print("Example 4: Different Search Types")
    print("="*60)
    
    query = "artificial intelligence"
    
    search_types = ["semantic", "keyword", "hybrid"]
    for search_type in search_types:
        print(f"\n{search_type.capitalize()} Search:")
        results = rag.search_only(query, top_k=2, search_type=search_type)
        print(f"   Found {len(results)} results")
        if results:
            avg_score = sum(r['score'] for r in results) / len(results)
            print(f"   Average score: {avg_score:.3f}")
    
    print("\n" + "="*60)
    print("✅ Basic RAG Implementation Example Completed!")
    print("="*60)
    print("\n💡 Key Takeaways:")
    print("  • RAG combines retrieval, augmentation, and generation")
    print("  • Each step can be used independently or together")
    print("  • The system provides source-based, accurate answers")
    print("  • Different search types offer different strengths")

if __name__ == "__main__":
    main() 