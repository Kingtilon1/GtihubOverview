# GitHub Repository Assistant using NVIDIA NIMs

A RAG-based tool that helps users understand GitHub repositories by answering questions about contribution guidelines, setup, and project information using NVIDIA's advanced language models.

## Features
- Process GitHub repository documentation (README, CONTRIBUTING, CODE_OF_CONDUCT, LICENSE)
- Store processed information using Pinecone vector database
- Answer questions about repositories using NVIDIA's LLM models
- Real-time processing of any public GitHub repository

## Tech Stack
- **NVIDIA NIMs**: Embeddings and LLM for text processing
- **Pinecone**: Vector database for storing embeddings
- **Flask**: Backend server
- **Next.js**: Frontend interface
- **Material UI**: UI components

## Prerequisites
- Python 3.10+
- Node.js 16+
- GitHub account
- NVIDIA API key (from NVIDIA AI Playground)
- Pinecone API key (free tier works)

## Setup

### Backend Setup
1. Clone the repository
2. Navigate to backend directory and Create virtual environment:
```bash
cd backend
bashCopypython -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```
3: Install dependencies:
```bash
pip install -r requirements.txt
```

4: Create .env file in backend directory:
```bash
GITHUB_TOKEN=your_github_token
NVIDIA_API_KEY=your_nvidia_api_key
PINECONE_API_KEY=your_pinecone_api_key
```
### Frontend Setup
Navigate to project root:
```bash
cd ..  # If you're in backend directory
```
### Running the Application

Start Flask backend (in backend directory):
```bash
python llama.py
```
Start Next.js frontend (in root directory):
```bash
npm run dev
```
Open http://localhost:3000 in your browser

### Usage
Enter a GitHub repository URL (e.g., https://github.com/tensorflow/tensorflow)
Click "Process Repository" to analyze the documentation
Once processed, enter your question about the repository
Click "Ask Question" to get an answer based on the repository's documentation

### Project Structure
Copy/
├── backend/
│   ├── llama.py        # Flask backend
│   └── requirements.txt
├── src/
│   └── app/
│       ├── page.js     # Main frontend page
│       └── api/        # API routes
└── package.json

### API Endpoints
All backend endpoints run on the Flask server (default: http://127.0.0.1:5000)

### Repository Processing

URL: http://127.0.0.1:5000/repo
Method: POST
Body:

```json
{
    "repo_url": "https://github.com/owner/repository"
}
```

### Query Repository

URL: http://127.0.0.1:5000/query
Method: POST
Body:

```json
{
    "question": "How do I contribute to this project?",
    "repo_url": "https://github.com/owner/repository"
}
```

Note: If your Flask server runs on a different port, update the URLs accordingly in both the frontend code (page.js) and when making direct API calls.
Technologies Used

NVIDIA NIM Microservices for embeddings and LLM

Embedding model: nvidia/nv-embedqa-e5-v5
LLM model: meta/llama3-70b-instruct


Pinecone for vector storage
Flask for API endpoints
Next.js with Material UI for frontend

Error Handling

Handles missing documentation files gracefully
Provides clear error messages for invalid URLs
Manages API rate limits and timeouts

Future Improvements

Support for private repositories
Additional documentation file types
Enhanced error handling
Response caching


