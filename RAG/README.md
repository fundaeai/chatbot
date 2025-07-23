# RAG System - Production-Ready Implementation

A clean, organized implementation of Retrieval-Augmented Generation (RAG) with centralized hyperparameters and prompts for easy experimentation.

## 🏗️ **Organized Structure**

```
RAG/
├── 🔧 Core Components (Algorithm Pipeline)
│   ├── __init__.py
│   ├── retrieval.py         # Step 1: Document retrieval
│   ├── augmentation.py      # Step 2: Context building
│   ├── generation.py        # Step 3: Answer generation
│   └── rag_orchestrator.py  # Combines all three steps
│
├── ⚙️ Configuration
│   ├── __init__.py
│   ├── hyperparameters.py   # ALL configurable parameters
│   ├── prompts.py          # ALL AI prompts
│   └── config.py           # Environment & system config
│
├── 🌐 API Interface
│   ├── __init__.py
│   └── rag_api.py          # FastAPI server
│
├── 📚 Documentation
│   ├── README.md           # Detailed documentation
│   ├── API_TESTING.md      # Comprehensive API testing guide
│   └── example.py          # Usage examples
│
└── 📦 Dependencies
    └── requirements.txt    # All dependencies
```

## 🔍 **Three Clear RAG Steps**

### **Step 1: Retrieval** (`core/retrieval.py`)
- Searches through document database
- Finds relevant chunks based on your question
- Uses semantic similarity and keyword matching
- **Hyperparameters**: `top_k`, `search_type`, `min_similarity_score`

### **Step 2: Augmentation** (`core/augmentation.py`)
- Takes the retrieved chunks
- Builds context by combining relevant information
- Formats: `[Source: doc1.pdf, Page: 2, Score: 0.95]`
- **Hyperparameters**: `context_length`, `source_format`, `separators`

### **Step 3: Generation** (`core/generation.py`)
- Uses GPT-4 to generate answers
- Combines the augmented context with your question
- Produces accurate, source-based responses
- **Hyperparameters**: `temperature`, `max_tokens`, `top_p`

## ⚙️ **Centralized Configuration**

### **Hyperparameters** (`config/hyperparameters.py`)
All configurable parameters in one place:

```python
from config.hyperparameters import RAGHyperparameters

# Retrieval parameters
RAGHyperparameters.DEFAULT_TOP_K = 5
RAGHyperparameters.MIN_SIMILARITY_SCORE = 0.7

# Augmentation parameters  
RAGHyperparameters.DEFAULT_CONTEXT_LENGTH = 4000
RAGHyperparameters.SOURCE_FORMAT = "[Source: {filename}, Page: {page}, Score: {score:.3f}]"

# Generation parameters
RAGHyperparameters.DEFAULT_TEMPERATURE = 0.7
RAGHyperparameters.DEFAULT_MAX_TOKENS = 500
```

### **Prompts** (`config/prompts.py`)
All AI prompts in one place:

```python
from config.prompts import RAGPrompts

# Core RAG prompts
RAGPrompts.RAG_SYSTEM_PROMPT
RAGPrompts.RAG_USER_PROMPT_TEMPLATE

# Specialized prompts
RAGPrompts.TECHNICAL_QUESTION_PROMPT
RAGPrompts.ACADEMIC_QUESTION_PROMPT
RAGPrompts.FACTUAL_QUESTION_PROMPT
```

## 🚀 **Quick Start**

### 1. Install Dependencies
```bash
cd RAG
pip install -r requirements.txt
```

### 2. Configure Environment
Create `.env` file:
```env
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_ENDPOINT=your-endpoint
AZURE_SEARCH_ENDPOINT=your-search-endpoint
AZURE_SEARCH_KEY=your-search-key
```

### 3. Start the API Server
```bash
python main.py
# Available at: http://localhost:8002
```

### 4. Test with Postman/FastAPI
- **FastAPI Interactive Docs**: http://localhost:8002/docs
- **API Testing Guide**: See `docs/API_TESTING.md` for detailed examples

## 🎯 **Simple Usage**

### **Complete RAG Pipeline**
```python
from core.rag_orchestrator import RAGOrchestrator

# Initialize RAG system
rag = RAGOrchestrator()

# Ask a question (handles all 3 steps automatically)
result = rag.ask("What is machine learning?")
print(result['answer'])
print(f"Confidence: {result['confidence']}")
print(f"Sources: {len(result['sources'])}")
```

### **Individual Steps**
```python
# Step 1: Retrieval only
from core.rag_orchestrator import RAGOrchestrator
rag = RAGOrchestrator()
chunks = rag.search_only("machine learning", top_k=5)

# Step 2: Augmentation only
from core.augmentation import AugmentationComponent
augmentation = AugmentationComponent()
context = augmentation.augment(chunks, max_length=4000)

# Step 3: Generation only
from core.generation import GenerationComponent
generation = GenerationComponent()
answer = generation.generate("What is ML?", context)
```

## 🔧 **API Endpoints**

### **Complete RAG Pipeline**
```bash
POST /ask
{
  "question": "What is machine learning?",
  "top_k": 5,
  "search_type": "hybrid",
  "context_length": 4000,
  "temperature": 0.7,
  "max_tokens": 500
}
```

### **Search Only (Step 1)**
```bash
POST /search
{
  "query": "machine learning",
  "top_k": 5,
  "search_type": "hybrid"
}
```

### **System Info**
```bash
GET /health
GET /statistics
```

## 🧪 **Experimentation Made Easy**

### **Tweak Hyperparameters**
Edit `config/hyperparameters.py` to experiment with:
- Retrieval: `DEFAULT_TOP_K`, `MIN_SIMILARITY_SCORE`
- Augmentation: `DEFAULT_CONTEXT_LENGTH`, `SOURCE_FORMAT`
- Generation: `DEFAULT_TEMPERATURE`, `MAX_MAX_TOKENS`
- Performance: `CACHE_ENABLED`, `MAX_PROCESSING_TIME`

### **Customize Prompts**
Edit `config/prompts.py` to experiment with:
- Core prompts: `RAG_SYSTEM_PROMPT`, `RAG_USER_PROMPT_TEMPLATE`
- Specialized prompts: `TECHNICAL_QUESTION_PROMPT`, `ACADEMIC_QUESTION_PROMPT`
- Enhanced prompts: `DETAILED_ANALYSIS_PROMPT`, `COMPARATIVE_ANALYSIS_PROMPT`

### **API Testing with Postman/FastAPI**
The FastAPI server provides:
- Interactive API documentation at `/docs`
- All endpoints for testing
- Request/response validation
- Easy integration with Postman
- Comprehensive testing guide in `docs/API_TESTING.md`

## 📊 **Production Features**

### **Monitoring & Validation**
- Pipeline health checks
- Component validation
- Performance metrics
- Error handling with retries

### **Scalability**
- Configurable batch sizes
- Memory limits
- Processing timeouts
- Concurrent request handling

### **Quality Assurance**
- Confidence scoring
- Answer validation
- Context relevance assessment
- Source attribution

## 🔄 **How RAG Works**

```
Question → Retrieval → Augmentation → Generation → Answer
    ↓           ↓           ↓           ↓
"What is ML?" → Find docs → Build context → GPT-4 → "ML is..."
```

### **Step-by-Step Process:**

1. **User asks a question**: "What is machine learning?"

2. **Retrieval**: 
   - System searches document database
   - Finds chunks about machine learning
   - Returns relevant passages with scores

3. **Augmentation**:
   - Combines retrieved chunks into context
   - Formats: `[Source: doc1.pdf, Page: 2, Score: 0.95]`
   - Prepares for language model

4. **Generation**:
   - Sends to GPT-4: "Context: [chunks]... Question: What is ML?"
   - GPT-4 generates answer based on context
   - Returns: "Based on the documents, machine learning is..."

## 🎯 **Key Benefits**

1. **Clear Separation**: Each step is in its own file with clear responsibilities
2. **Centralized Configuration**: All hyperparameters and prompts in one place
3. **Easy Experimentation**: Tweak parameters without touching core logic
4. **Production Ready**: Proper error handling, validation, and monitoring
5. **Modular Design**: Use each component independently or together
6. **Source-Based**: Always provides sources for answers

This implementation makes RAG **simple, clear, and production-ready** - perfect for experimentation and deployment! 