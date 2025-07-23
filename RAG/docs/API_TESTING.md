# API Testing Guide

Comprehensive guide for testing the RAG API using Postman or FastAPI interactive docs.

## 🚀 **Quick Start**

### 1. Start the API Server
```bash
cd RAG
python main.py
```

### 2. Access API Documentation
- **FastAPI Interactive Docs**: http://localhost:8002/docs
- **ReDoc Documentation**: http://localhost:8002/redoc
- **OpenAPI JSON**: http://localhost:8002/openapi.json

## 🔧 **API Endpoints**

### **Health Check**
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "retrieval": {...},
    "augmentation": {...},
    "generation": {...}
  },
  "config": {...}
}
```

### **System Statistics**
```http
GET /statistics
```

**Response:**
```json
{
  "pipeline": {
    "retrieval": {...},
    "augmentation": {...},
    "generation": {...}
  },
  "config": {...}
}
```

### **Search Documents (Step 1: Retrieval)**
```http
POST /search
Content-Type: application/json

{
  "query": "machine learning algorithms",
  "top_k": 5,
  "search_type": "hybrid",
  "min_score": 0.7
}
```

**Response:**
```json
{
  "results": [
    {
      "content": "Machine learning is a subset of artificial intelligence...",
      "filename": "ml_intro.pdf",
      "chunk_index": 3,
      "page_number": 2,
      "chunk_type": "text",
      "tags": ["machine-learning", "ai"],
      "score": 0.95
    }
  ],
  "total_results": 5,
  "search_time": 0.15,
  "search_type": "hybrid"
}
```

### **Ask Questions (Complete RAG Pipeline)**
```http
POST /ask
Content-Type: application/json

{
  "question": "What are the main types of machine learning?",
  "top_k": 5,
  "search_type": "hybrid",
  "context_length": 4000,
  "temperature": 0.7,
  "max_tokens": 500
}
```

**Response:**
```json
{
  "answer": "Based on the retrieved documents, there are three main types of machine learning...",
  "sources": [
    {
      "filename": "ml_intro.pdf",
      "page": 2,
      "content": "The three main types are supervised, unsupervised, and reinforcement learning...",
      "score": 0.95,
      "chunk_type": "text"
    }
  ],
  "confidence": 0.92,
  "processing_time": 2.3,
  "search_results_count": 5,
  "context_length": 3500,
  "search_type": "hybrid"
}
```

## 📋 **Postman Collection**

### **Import this collection into Postman:**

```json
{
  "info": {
    "name": "RAG API Testing",
    "description": "Complete RAG system API endpoints"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": "http://localhost:8002/health"
      }
    },
    {
      "name": "Get Statistics",
      "request": {
        "method": "GET",
        "url": "http://localhost:8002/statistics"
      }
    },
    {
      "name": "Search Documents",
      "request": {
        "method": "POST",
        "url": "http://localhost:8002/search",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"query\": \"machine learning algorithms\",\n  \"top_k\": 5,\n  \"search_type\": \"hybrid\",\n  \"min_score\": 0.7\n}"
        }
      }
    },
    {
      "name": "Ask Question",
      "request": {
        "method": "POST",
        "url": "http://localhost:8002/ask",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"question\": \"What are the main types of machine learning?\",\n  \"top_k\": 5,\n  \"search_type\": \"hybrid\",\n  \"context_length\": 4000,\n  \"temperature\": 0.7,\n  \"max_tokens\": 500\n}"
        }
      }
    }
  ]
}
```

## 🧪 **Testing Scenarios**

### **1. Basic Functionality Test**
```bash
# Test health endpoint
curl http://localhost:8002/health

# Test search endpoint
curl -X POST http://localhost:8002/search \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "top_k": 3}'

# Test ask endpoint
curl -X POST http://localhost:8002/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is machine learning?", "top_k": 5}'
```

### **2. Parameter Testing**

**Different Search Types:**
```json
{"query": "machine learning", "search_type": "semantic"}
{"query": "machine learning", "search_type": "keyword"}
{"query": "machine learning", "search_type": "hybrid"}
```

**Different Context Lengths:**
```json
{"question": "What is ML?", "context_length": 2000}
{"question": "What is ML?", "context_length": 4000}
{"question": "What is ML?", "context_length": 6000}
```

**Different Generation Parameters:**
```json
{"question": "What is ML?", "temperature": 0.3, "max_tokens": 300}
{"question": "What is ML?", "temperature": 0.7, "max_tokens": 500}
{"question": "What is ML?", "temperature": 1.0, "max_tokens": 800}
```

### **3. Error Handling Test**
```json
// Empty question
{"question": ""}

// Very long question
{"question": "This is a very long question that exceeds the maximum allowed length..."}

// Invalid parameters
{"question": "What is ML?", "top_k": 100, "temperature": 2.0}
```

## 📊 **Expected Response Times**

- **Health Check**: < 100ms
- **Statistics**: < 200ms
- **Search Only**: 100-500ms
- **Complete RAG**: 2-5 seconds

## 🔍 **Response Validation**

### **Search Response Validation**
- ✅ `results` array contains document chunks
- ✅ Each result has `content`, `filename`, `page_number`, `score`
- ✅ `total_results` matches array length
- ✅ `search_time` is reasonable (< 1 second)

### **Ask Response Validation**
- ✅ `answer` is not empty and relevant
- ✅ `sources` array contains source documents
- ✅ `confidence` is between 0.0 and 1.0
- ✅ `processing_time` is reasonable (< 10 seconds)
- ✅ `context_length` is within limits

## 🐛 **Troubleshooting**

### **Common Issues**

**1. Connection Refused**
```bash
# Check if server is running
ps aux | grep python
# Restart server
python main.py
```

**2. Authentication Errors**
```bash
# Check environment variables
echo $AZURE_OPENAI_API_KEY
echo $AZURE_SEARCH_ENDPOINT
```

**3. No Results Found**
```bash
# Check if documents are indexed
curl http://localhost:8002/statistics
# Verify search index has documents
```

**4. Slow Response Times**
```bash
# Check system resources
top
# Reduce context_length or top_k parameters
```

## 📝 **Testing Checklist**

- [ ] Health endpoint returns 200 OK
- [ ] Statistics endpoint returns pipeline info
- [ ] Search endpoint returns relevant documents
- [ ] Ask endpoint returns coherent answers
- [ ] Error handling works for invalid inputs
- [ ] Response times are within acceptable limits
- [ ] All required fields are present in responses
- [ ] Confidence scores are reasonable
- [ ] Source attribution is accurate

## 🎯 **Performance Testing**

### **Load Testing**
```bash
# Test with multiple concurrent requests
for i in {1..10}; do
  curl -X POST http://localhost:8002/ask \
    -H "Content-Type: application/json" \
    -d '{"question": "What is machine learning?"}' &
done
wait
```

### **Stress Testing**
```bash
# Test with large context
curl -X POST http://localhost:8002/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is ML?", "context_length": 8000, "top_k": 20}'
```

This guide provides everything you need to thoroughly test the RAG API using Postman or any HTTP client! 