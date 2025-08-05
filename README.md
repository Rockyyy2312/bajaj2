# Insurance LLM Backend

An intelligent insurance document processing system that uses LLM (Large Language Models) to analyze insurance queries and provide coverage decisions.

## 🎯 Features

- **Natural Language Query Processing**: Understands unstructured insurance queries
- **Entity Extraction**: Automatically extracts age, gender, medical conditions, locations, and policy details
- **Semantic Search**: Uses Pinecone vector database for intelligent clause matching
- **LLM-Powered Analysis**: Leverages Groq's LLaMA3-70B for intelligent decision making
- **PDF Document Processing**: Extracts and processes insurance documents
- **Structured Responses**: Provides detailed coverage decisions with justifications

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │  Document Proc  │    │  Embedding Svc  │
│                 │    │                 │    │                 │
│  - API Routes   │◄──►│  - PDF Extract  │◄──►│  - Vector DB    │
│  - Request/Resp │    │  - Clause Detect│    │  - Similarity   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   LLM Service   │    │  Clause Master  │    │  Pinecone DB    │
│                 │    │                 │    │                 │
│  - Groq LLM     │    │  - Rule Engine  │    │  - Vector Store │
│  - Entity Extr  │    │  - Coverage Eval│    │  - Metadata     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Groq API Key
- Pinecone API Key
- MongoDB (optional)

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd insurance-llm-backend
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file:

   ```env
   GROQ_API_KEY=your_groq_api_key_here
   PINECONE_API_KEY=your_pinecone_api_key_here
   PINECONE_ENVIRONMENT=us-east-1
   MONGODB_URL=mongodb://localhost:27017/insurance_db
   ```

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

## 📚 API Endpoints

### 1. Analyze Insurance Query

**POST** `/analyze/`

Analyzes a natural language insurance query and provides coverage decision.

**Request:**

```json
{
  "query": "46-year-old male, knee surgery in Pune, 3-month-old insurance policy"
}
```

**Response:**

```json
{
  "query": "46-year-old male, knee surgery in Pune, 3-month-old insurance policy",
  "extracted_entities": {
    "age": 46,
    "gender": "male",
    "condition": "knee surgery",
    "location": "Pune",
    "policy_duration": "3",
    "coverage_type": null
  },
  "matched_clauses": [
    {
      "clause_id": "clause_5.1",
      "clause_title": "Surgical Procedures Coverage",
      "clause_content": "Knee surgery is covered under this policy...",
      "relevance_score": 0.85
    }
  ],
  "decision": {
    "decision": "rejected",
    "amount": null,
    "justification": "Waiting period not met. Required: 12 months, Current: 3 months",
    "mapped_clauses": ["clause_5.1", "clause_2.3"],
    "confidence_score": 0.8,
    "waiting_period_info": "Policy is only 3 months old, but 12 months waiting period is required for knee surgery",
    "exclusions": []
  },
  "processing_time": 2.34
}
```

### 2. Upload Insurance Document

**POST** `/upload-document/`

Upload and process insurance documents (PDF format).

**Request:** Multipart form with PDF file

**Response:**

```json
{
  "document_id": "uuid-here",
  "filename": "insurance_policy.pdf",
  "pages_processed": 5,
  "clauses_extracted": 12,
  "status": "processed"
}
```

### 3. Health Check

**GET** `/health/`

Check system health and service status.

**Response:**

```json
{
  "status": "healthy",
  "vector_database": {
    "total_vectors": 150,
    "dimension": 384
  },
  "services": {
    "document_processor": "operational",
    "embedding_service": "operational",
    "llm_service": "operational"
  }
}
```

### 4. Document Statistics

**GET** `/documents/stats/`

Get statistics about stored documents and clauses.

### 5. Delete Document

**DELETE** `/documents/{document_id}/`

Delete a document and its associated clauses.

## 🔧 Configuration

### Environment Variables

| Variable               | Description                    | Default                               |
| ---------------------- | ------------------------------ | ------------------------------------- |
| `GROQ_API_KEY`         | Groq API key for LLM access    | Required                              |
| `PINECONE_API_KEY`     | Pinecone API key for vector DB | Required                              |
| `PINECONE_ENVIRONMENT` | Pinecone environment           | `us-east-1`                           |
| `PINECONE_INDEX_NAME`  | Pinecone index name            | `project`                             |
| `MONGODB_URL`          | MongoDB connection string      | `mongodb://localhost:27017/hackrx_db` |
| `CHUNK_SIZE`           | Text chunk size for processing | `1000`                                |
| `CHUNK_OVERLAP`        | Text chunk overlap             | `200`                                 |
| `VECTOR_DIMENSION`     | Embedding dimension            | `384`                                 |

### Model Configuration

- **LLM Model**: LLaMA3-70B via Groq
- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Vector Database**: Pinecone
- **Document Processing**: PyMuPDF for PDF extraction

## 🧪 Testing

Run the test script to verify system functionality:

```bash
python test_system.py
```

This will test:

- Entity extraction from queries
- Clause matching and similarity search
- LLM-powered decision making
- Document processing capabilities

## 📊 Example Usage

### Python Client Example

```python
import requests
import json

# Analyze insurance query
query_data = {
    "query": "46-year-old male, knee surgery in Pune, 3-month-old insurance policy"
}

response = requests.post(
    "http://localhost:8000/analyze/",
    json=query_data
)

result = response.json()
print(f"Decision: {result['decision']['decision']}")
print(f"Amount: {result['decision']['amount']}")
print(f"Justification: {result['decision']['justification']}")
```

### cURL Example

```bash
curl -X POST "http://localhost:8000/analyze/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "46-year-old male, knee surgery in Pune, 3-month-old insurance policy"
  }'
```

## 🔍 How It Works

### 1. Query Processing

- Takes natural language insurance query
- Extracts key entities (age, gender, condition, location, policy duration)
- Uses regex patterns and LLM for entity extraction

### 2. Semantic Search

- Converts query to embedding vector
- Searches Pinecone vector database for similar clauses
- Returns top-k most relevant insurance clauses

### 3. Decision Making

- Sends query + matched clauses to Groq LLM
- LLM analyzes coverage eligibility based on:
  - Age requirements (18-65 years)
  - Waiting periods (3/12/24 months)
  - Coverage limits from clauses
  - Exclusions and limitations

### 4. Response Generation

- Provides structured JSON response with:
  - Coverage decision (approved/rejected/pending)
  - Coverage amount
  - Detailed justification
  - Mapped clause references
  - Confidence score

## 🛠️ Development

### Project Structure

```
insurance-llm-backend/
├── app/
│   ├── api/
│   │   └── endpoints.py          # FastAPI routes
│   ├── models/
│   │   └── schemas.py            # Pydantic models
│   ├── services/
│   │   ├── document_processor.py # PDF processing
│   │   ├── embedding_service.py  # Vector operations
│   │   ├── llm_service.py        # LLM interactions
│   │   └── clause_master.py      # Clause management
│   ├── utils/
│   │   ├── config.py             # Configuration
│   │   └── helpers.py            # Utility functions
│   └── main.py                   # FastAPI app
├── requirements.txt
├── test_system.py
└── README.md
```

### Adding New Features

1. **New Entity Types**: Update `ExtractedEntities` in `schemas.py`
2. **New Clause Types**: Add patterns in `clause_master.py`
3. **New API Endpoints**: Add routes in `endpoints.py`
4. **New LLM Prompts**: Modify prompts in `llm_service.py`

## 🚨 Error Handling

The system includes comprehensive error handling:

- **API Errors**: Proper HTTP status codes and error messages
- **LLM Failures**: Fallback to rule-based decision making
- **Vector DB Errors**: Graceful degradation with mock data
- **Document Processing**: Validation and error reporting

## 📈 Performance

- **Response Time**: ~2-5 seconds per query
- **Concurrent Requests**: Supports multiple simultaneous queries
- **Vector Search**: Sub-second similarity search
- **LLM Processing**: Optimized prompts for faster responses

## 🔐 Security

- **API Key Management**: Environment variables for sensitive data
- **Input Validation**: Pydantic models for request validation
- **Error Sanitization**: No sensitive data in error messages
- **File Upload Security**: PDF validation and size limits

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:

- Create an issue in the repository
- Check the documentation
- Review the test examples

---

**Built with ❤️ using FastAPI, Groq, Pinecone, and Python**
