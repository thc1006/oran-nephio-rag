# Integration Examples

This guide provides comprehensive examples for integrating with the O-RAN × Nephio RAG API using various methods including CLI tools, Python SDK, JavaScript, and cURL.

## Table of Contents

- [cURL Examples](#curl-examples)
- [Python SDK Examples](#python-sdk-examples)
- [JavaScript/Node.js Examples](#javascriptnodejs-examples)
- [CLI Integration](#cli-integration)
- [Postman Collection](#postman-collection)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)

## cURL Examples

### Basic Query

```bash
# Simple O-RAN question
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "query": "What is the O-RAN architecture?",
    "k": 5,
    "include_sources": true
  }' | jq '.'

# Nephio deployment question
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How does Nephio handle network function scaling?",
    "k": 8,
    "context_length": 6000,
    "include_sources": true
  }' | jq '.answer'
```

### Advanced Query with Streaming

```bash
# Stream response for long queries
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain the complete O-RAN integration process with Nephio",
    "k": 10,
    "model": "claude-sonnet-4",
    "stream": true,
    "context_length": 8000
  }' --no-buffer
```

### Document Search

```bash
# Basic search
curl -X POST "http://localhost:8000/api/v1/query/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "network function scaling",
    "k": 10,
    "score_threshold": 0.7
  }' | jq '.results[].metadata.title'

# Filtered search by source type
curl -X POST "http://localhost:8000/api/v1/query/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Nephio deployment",
    "k": 15,
    "source_types": ["nephio"],
    "priority_range": [1, 2],
    "score_threshold": 0.8
  }' | jq '.total_found'
```

### Bulk Query Processing

```bash
# Process multiple queries
curl -X POST "http://localhost:8000/api/v1/query/bulk" \
  -H "Content-Type: application/json" \
  -d '{
    "queries": [
      "What is O-RAN?",
      "How does Nephio work?",
      "What is O2IMS?",
      "How to deploy Free5GC with Nephio?"
    ],
    "k": 5,
    "include_sources": false
  }' | jq '.results[].answer'
```

### System Management

```bash
# Check system health
curl "http://localhost:8000/health" | jq '.'

# Get system status
curl "http://localhost:8000/api/v1/system/status" \
  -H "Authorization: Bearer YOUR_API_KEY" | jq '.'

# Get configuration
curl "http://localhost:8000/api/v1/system/config" \
  -H "Authorization: Bearer YOUR_API_KEY" | jq '.'

# Get metrics
curl "http://localhost:8000/api/v1/system/metrics" \
  -H "Authorization: Bearer YOUR_API_KEY" | jq '.'

# Refresh document database
curl -X POST "http://localhost:8000/api/v1/documents/refresh" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "force_rebuild": true,
    "source_types": ["nephio", "oran_sc"]
  }' | jq '.'
```

## Python SDK Examples

### Basic Client Implementation

```python
import requests
import json
import time
from typing import List, Dict, Optional, Union
from dataclasses import dataclass

@dataclass
class QueryResponse:
    answer: str
    sources: List[Dict]
    query_time: float
    context_used: int
    generation_method: str

class ORANNephioClient:
    """Python client for O-RAN × Nephio RAG API"""

    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()

        # Set default headers
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "oran-nephio-client/1.0.0"
        })

        if api_key:
            self.session.headers["Authorization"] = f"Bearer {api_key}"

    def query(self,
              question: str,
              k: int = 5,
              include_sources: bool = True,
              model: Optional[str] = None,
              context_length: Optional[int] = None) -> QueryResponse:
        """Query the RAG system"""

        payload = {
            "query": question,
            "k": k,
            "include_sources": include_sources
        }

        if model:
            payload["model"] = model
        if context_length:
            payload["context_length"] = context_length

        response = self.session.post(
            f"{self.base_url}/api/v1/query",
            json=payload
        )
        response.raise_for_status()

        data = response.json()
        return QueryResponse(
            answer=data["answer"],
            sources=data.get("sources", []),
            query_time=data["query_time"],
            context_used=data["context_used"],
            generation_method=data["generation_method"]
        )

    def search(self,
               query: str,
               k: int = 10,
               source_types: Optional[List[str]] = None,
               score_threshold: float = 0.0) -> Dict:
        """Search documents without generating answers"""

        payload = {
            "query": query,
            "k": k,
            "score_threshold": score_threshold
        }

        if source_types:
            payload["source_types"] = source_types

        response = self.session.post(
            f"{self.base_url}/api/v1/query/search",
            json=payload
        )
        response.raise_for_status()
        return response.json()

    def bulk_query(self,
                   queries: List[str],
                   k: int = 5,
                   include_sources: bool = False) -> List[QueryResponse]:
        """Process multiple queries in batch"""

        payload = {
            "queries": queries,
            "k": k,
            "include_sources": include_sources
        }

        response = self.session.post(
            f"{self.base_url}/api/v1/query/bulk",
            json=payload
        )
        response.raise_for_status()

        data = response.json()
        return [
            QueryResponse(
                answer=result["answer"],
                sources=result.get("sources", []),
                query_time=result["query_time"],
                context_used=result["context_used"],
                generation_method=result["generation_method"]
            )
            for result in data["results"]
        ]

    def get_health(self) -> Dict:
        """Get system health status"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def get_system_status(self) -> Dict:
        """Get detailed system status"""
        response = self.session.get(f"{self.base_url}/api/v1/system/status")
        response.raise_for_status()
        return response.json()

    def get_config(self) -> Dict:
        """Get system configuration"""
        response = self.session.get(f"{self.base_url}/api/v1/system/config")
        response.raise_for_status()
        return response.json()

    def refresh_documents(self, force_rebuild: bool = False) -> Dict:
        """Refresh the document database"""
        payload = {"force_rebuild": force_rebuild}
        response = self.session.post(
            f"{self.base_url}/api/v1/documents/refresh",
            json=payload
        )
        response.raise_for_status()
        return response.json()

# Example usage
def main():
    # Initialize client
    client = ORANNephioClient(
        base_url="http://localhost:8000",
        api_key="your_api_key_here"  # Optional
    )

    try:
        # Check system health
        health = client.get_health()
        print(f"System status: {health['status']}")

        # Query about O-RAN architecture
        response = client.query(
            "What are the main components of O-RAN architecture?",
            k=8,
            include_sources=True
        )

        print(f"Answer: {response.answer}")
        print(f"Query time: {response.query_time:.2f}s")
        print(f"Sources: {len(response.sources)}")

        # Search for Nephio documentation
        search_results = client.search(
            "Nephio package specialization",
            k=10,
            source_types=["nephio"],
            score_threshold=0.7
        )

        print(f"Found {search_results['total_found']} relevant documents")

        # Batch process multiple queries
        questions = [
            "What is O2IMS?",
            "How does Nephio automate deployment?",
            "What are the benefits of O-RAN?"
        ]

        batch_results = client.bulk_query(questions, k=3)
        for i, result in enumerate(batch_results):
            print(f"Q{i+1}: {result.answer[:100]}...")

    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
```

### Async Python Client

```python
import aiohttp
import asyncio
from typing import List, Dict, Optional

class AsyncORANNephioClient:
    """Async Python client for O-RAN × Nephio RAG API"""

    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.headers = {"Content-Type": "application/json"}

        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    async def query(self, question: str, **kwargs) -> Dict:
        """Async query method"""
        payload = {"query": question, **kwargs}

        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(
                f"{self.base_url}/api/v1/query",
                json=payload
            ) as response:
                response.raise_for_status()
                return await response.json()

    async def concurrent_queries(self, questions: List[str]) -> List[Dict]:
        """Process multiple queries concurrently"""
        tasks = [self.query(q) for q in questions]
        return await asyncio.gather(*tasks)

# Example usage
async def async_example():
    client = AsyncORANNephioClient()

    # Concurrent queries
    questions = [
        "What is O-RAN architecture?",
        "How does Nephio work?",
        "What is Free5GC integration?"
    ]

    results = await client.concurrent_queries(questions)
    for i, result in enumerate(results):
        print(f"Q{i+1}: {result['answer'][:100]}...")

# Run async example
# asyncio.run(async_example())
```

## JavaScript/Node.js Examples

### Basic Node.js Client

```javascript
const axios = require('axios');

class ORANNephioClient {
    constructor(baseUrl = 'http://localhost:8000', apiKey = null) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.client = axios.create({
            baseURL: this.baseUrl,
            headers: {
                'Content-Type': 'application/json',
                'User-Agent': 'oran-nephio-client-js/1.0.0',
                ...(apiKey && { 'Authorization': `Bearer ${apiKey}` })
            },
            timeout: 30000
        });

        // Add response interceptor for error handling
        this.client.interceptors.response.use(
            response => response,
            error => {
                console.error('API Error:', error.response?.data || error.message);
                throw error;
            }
        );
    }

    async query(question, options = {}) {
        const payload = {
            query: question,
            k: options.k || 5,
            include_sources: options.includeSources !== false,
            ...options
        };

        const response = await this.client.post('/api/v1/query', payload);
        return response.data;
    }

    async search(query, options = {}) {
        const payload = {
            query,
            k: options.k || 10,
            score_threshold: options.scoreThreshold || 0.0,
            ...options
        };

        const response = await this.client.post('/api/v1/query/search', payload);
        return response.data;
    }

    async bulkQuery(queries, options = {}) {
        const payload = {
            queries,
            k: options.k || 5,
            include_sources: options.includeSources || false
        };

        const response = await this.client.post('/api/v1/query/bulk', payload);
        return response.data;
    }

    async getHealth() {
        const response = await this.client.get('/health');
        return response.data;
    }

    async getSystemStatus() {
        const response = await this.client.get('/api/v1/system/status');
        return response.data;
    }

    async refreshDocuments(forceRebuild = false) {
        const response = await this.client.post('/api/v1/documents/refresh', {
            force_rebuild: forceRebuild
        });
        return response.data;
    }
}

// Example usage
async function main() {
    const client = new ORANNephioClient();

    try {
        // Check system health
        const health = await client.getHealth();
        console.log(`System status: ${health.status}`);

        // Query about O-RAN
        const result = await client.query(
            "What are the key benefits of O-RAN architecture?",
            { k: 8, includeSources: true }
        );

        console.log(`Answer: ${result.answer}`);
        console.log(`Query time: ${result.query_time.toFixed(2)}s`);
        console.log(`Sources: ${result.sources.length}`);

        // Search for documentation
        const searchResults = await client.search(
            "Nephio automation",
            { k: 10, sourceTypes: ["nephio"] }
        );

        console.log(`Found ${searchResults.total_found} documents`);

        // Bulk processing
        const questions = [
            "What is O2IMS?",
            "How to scale network functions?",
            "What is Nephio's role in 5G?"
        ];

        const bulkResults = await client.bulkQuery(questions);
        bulkResults.results.forEach((result, i) => {
            console.log(`Q${i+1}: ${result.answer.substring(0, 100)}...`);
        });

    } catch (error) {
        console.error('Error:', error.message);
    }
}

// Run example
main();
```

### Browser JavaScript Example

```html
<!DOCTYPE html>
<html>
<head>
    <title>O-RAN × Nephio RAG Client</title>
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
</head>
<body>
    <div id="app">
        <h1>O-RAN × Nephio RAG System</h1>

        <div>
            <label for="query">Ask a question:</label>
            <textarea id="query" rows="3" cols="50"
                placeholder="What is the O-RAN architecture?"></textarea>
            <br>
            <button onclick="submitQuery()">Submit Query</button>
        </div>

        <div id="results"></div>
    </div>

    <script>
        const API_BASE = 'http://localhost:8000';

        async function submitQuery() {
            const query = document.getElementById('query').value;
            const resultsDiv = document.getElementById('results');

            if (!query.trim()) {
                alert('Please enter a question');
                return;
            }

            resultsDiv.innerHTML = '<p>Processing query...</p>';

            try {
                const response = await axios.post(`${API_BASE}/api/v1/query`, {
                    query: query,
                    k: 5,
                    include_sources: true
                });

                const result = response.data;

                resultsDiv.innerHTML = `
                    <h3>Answer:</h3>
                    <p>${result.answer}</p>

                    <h4>Details:</h4>
                    <ul>
                        <li>Query time: ${result.query_time.toFixed(2)}s</li>
                        <li>Sources used: ${result.sources.length}</li>
                        <li>Generation method: ${result.generation_method}</li>
                    </ul>

                    <h4>Sources:</h4>
                    <ul>
                        ${result.sources.map(source => `
                            <li>
                                <strong>${source.metadata.title || 'Unknown'}</strong><br>
                                <small>Score: ${source.similarity_score?.toFixed(3)}</small><br>
                                <a href="${source.url}" target="_blank">${source.url}</a>
                            </li>
                        `).join('')}
                    </ul>
                `;

            } catch (error) {
                resultsDiv.innerHTML = `
                    <p style="color: red;">Error: ${error.message}</p>
                `;
            }
        }

        // Allow Enter key to submit
        document.getElementById('query').addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && e.ctrlKey) {
                submitQuery();
            }
        });
    </script>
</body>
</html>
```

## CLI Integration

### Bash Script Examples

```bash
#!/bin/bash

# oran-nephio-cli.sh - CLI wrapper for O-RAN × Nephio RAG API

API_BASE="${API_BASE:-http://localhost:8000}"
API_KEY="${API_KEY:-}"

# Set up authentication header
if [ -n "$API_KEY" ]; then
    AUTH_HEADER="Authorization: Bearer $API_KEY"
else
    AUTH_HEADER=""
fi

# Function to query the RAG system
query_rag() {
    local question="$1"
    local k="${2:-5}"

    curl -s -X POST "$API_BASE/api/v1/query" \
        -H "Content-Type: application/json" \
        ${AUTH_HEADER:+-H "$AUTH_HEADER"} \
        -d "{
            \"query\": \"$question\",
            \"k\": $k,
            \"include_sources\": true
        }" | jq -r '.answer'
}

# Function to search documents
search_docs() {
    local query="$1"
    local source_type="${2:-}"

    local payload="{\"query\": \"$query\", \"k\": 10}"

    if [ -n "$source_type" ]; then
        payload=$(echo "$payload" | jq ". + {\"source_types\": [\"$source_type\"]}")
    fi

    curl -s -X POST "$API_BASE/api/v1/query/search" \
        -H "Content-Type: application/json" \
        ${AUTH_HEADER:+-H "$AUTH_HEADER"} \
        -d "$payload" | jq -r '.results[] | "\(.metadata.title // "Unknown"): \(.similarity_score)"'
}

# Function to check system health
check_health() {
    curl -s "$API_BASE/health" | jq -r '.status'
}

# Function to get system status
system_status() {
    curl -s "$API_BASE/api/v1/system/status" \
        ${AUTH_HEADER:+-H "$AUTH_HEADER"} | jq '.'
}

# Main CLI interface
case "$1" in
    "query")
        if [ -z "$2" ]; then
            echo "Usage: $0 query \"your question\" [k]"
            exit 1
        fi
        query_rag "$2" "$3"
        ;;
    "search")
        if [ -z "$2" ]; then
            echo "Usage: $0 search \"search terms\" [source_type]"
            exit 1
        fi
        search_docs "$2" "$3"
        ;;
    "health")
        check_health
        ;;
    "status")
        system_status
        ;;
    *)
        echo "Usage: $0 {query|search|health|status}"
        echo ""
        echo "Examples:"
        echo "  $0 query \"What is O-RAN?\""
        echo "  $0 search \"Nephio deployment\" nephio"
        echo "  $0 health"
        echo "  $0 status"
        exit 1
        ;;
esac
```

### PowerShell Script

```powershell
# oran-nephio-cli.ps1 - PowerShell wrapper for O-RAN × Nephio RAG API

param(
    [Parameter(Mandatory=$true, Position=0)]
    [ValidateSet("query", "search", "health", "status")]
    [string]$Command,

    [Parameter(Position=1)]
    [string]$Query,

    [Parameter()]
    [int]$K = 5,

    [Parameter()]
    [string]$SourceType,

    [Parameter()]
    [string]$ApiBase = "http://localhost:8000",

    [Parameter()]
    [string]$ApiKey = $env:ORAN_API_KEY
)

# Set up headers
$Headers = @{
    "Content-Type" = "application/json"
}

if ($ApiKey) {
    $Headers["Authorization"] = "Bearer $ApiKey"
}

function Invoke-RagQuery {
    param($Question, $K)

    $Body = @{
        query = $Question
        k = $K
        include_sources = $true
    } | ConvertTo-Json

    try {
        $Response = Invoke-RestMethod -Uri "$ApiBase/api/v1/query" -Method POST -Headers $Headers -Body $Body
        return $Response.answer
    }
    catch {
        Write-Error "Query failed: $($_.Exception.Message)"
    }
}

function Search-Documents {
    param($SearchQuery, $SourceType)

    $Body = @{
        query = $SearchQuery
        k = 10
    }

    if ($SourceType) {
        $Body.source_types = @($SourceType)
    }

    $Body = $Body | ConvertTo-Json

    try {
        $Response = Invoke-RestMethod -Uri "$ApiBase/api/v1/query/search" -Method POST -Headers $Headers -Body $Body
        return $Response.results | ForEach-Object {
            "$($_.metadata.title): $($_.similarity_score)"
        }
    }
    catch {
        Write-Error "Search failed: $($_.Exception.Message)"
    }
}

function Get-SystemHealth {
    try {
        $Response = Invoke-RestMethod -Uri "$ApiBase/health" -Method GET
        return $Response.status
    }
    catch {
        Write-Error "Health check failed: $($_.Exception.Message)"
    }
}

function Get-SystemStatus {
    try {
        $Response = Invoke-RestMethod -Uri "$ApiBase/api/v1/system/status" -Method GET -Headers $Headers
        return $Response | ConvertTo-Json -Depth 5
    }
    catch {
        Write-Error "Status check failed: $($_.Exception.Message)"
    }
}

# Main logic
switch ($Command) {
    "query" {
        if (-not $Query) {
            Write-Error "Query parameter is required for query command"
            exit 1
        }
        Invoke-RagQuery -Question $Query -K $K
    }
    "search" {
        if (-not $Query) {
            Write-Error "Query parameter is required for search command"
            exit 1
        }
        Search-Documents -SearchQuery $Query -SourceType $SourceType
    }
    "health" {
        Get-SystemHealth
    }
    "status" {
        Get-SystemStatus
    }
}
```

## Postman Collection

```json
{
    "info": {
        "name": "O-RAN × Nephio RAG API",
        "description": "Complete API collection for O-RAN × Nephio RAG system",
        "version": "1.0.0"
    },
    "auth": {
        "type": "bearer",
        "bearer": [
            {
                "key": "token",
                "value": "{{api_key}}",
                "type": "string"
            }
        ]
    },
    "variable": [
        {
            "key": "base_url",
            "value": "http://localhost:8000",
            "type": "string"
        },
        {
            "key": "api_key",
            "value": "your_api_key_here",
            "type": "string"
        }
    ],
    "item": [
        {
            "name": "Health",
            "item": [
                {
                    "name": "Health Check",
                    "request": {
                        "method": "GET",
                        "header": [],
                        "url": {
                            "raw": "{{base_url}}/health",
                            "host": ["{{base_url}}"],
                            "path": ["health"]
                        }
                    }
                },
                {
                    "name": "Readiness Check",
                    "request": {
                        "method": "GET",
                        "header": [],
                        "url": {
                            "raw": "{{base_url}}/health/ready",
                            "host": ["{{base_url}}"],
                            "path": ["health", "ready"]
                        }
                    }
                }
            ]
        },
        {
            "name": "Queries",
            "item": [
                {
                    "name": "Basic Query",
                    "request": {
                        "method": "POST",
                        "header": [
                            {
                                "key": "Content-Type",
                                "value": "application/json"
                            }
                        ],
                        "body": {
                            "mode": "raw",
                            "raw": "{\n  \"query\": \"What is the O-RAN architecture?\",\n  \"k\": 5,\n  \"include_sources\": true\n}"
                        },
                        "url": {
                            "raw": "{{base_url}}/api/v1/query",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", "query"]
                        }
                    }
                },
                {
                    "name": "Advanced Query",
                    "request": {
                        "method": "POST",
                        "header": [
                            {
                                "key": "Content-Type",
                                "value": "application/json"
                            }
                        ],
                        "body": {
                            "mode": "raw",
                            "raw": "{\n  \"query\": \"How does Nephio handle network function scaling?\",\n  \"k\": 8,\n  \"model\": \"claude-sonnet-4\",\n  \"context_length\": 6000,\n  \"include_sources\": true\n}"
                        },
                        "url": {
                            "raw": "{{base_url}}/api/v1/query",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", "query"]
                        }
                    }
                },
                {
                    "name": "Document Search",
                    "request": {
                        "method": "POST",
                        "header": [
                            {
                                "key": "Content-Type",
                                "value": "application/json"
                            }
                        ],
                        "body": {
                            "mode": "raw",
                            "raw": "{\n  \"query\": \"network function scaling\",\n  \"k\": 10,\n  \"source_types\": [\"nephio\"],\n  \"score_threshold\": 0.7\n}"
                        },
                        "url": {
                            "raw": "{{base_url}}/api/v1/query/search",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", "query", "search"]
                        }
                    }
                },
                {
                    "name": "Bulk Query",
                    "request": {
                        "method": "POST",
                        "header": [
                            {
                                "key": "Content-Type",
                                "value": "application/json"
                            }
                        ],
                        "body": {
                            "mode": "raw",
                            "raw": "{\n  \"queries\": [\n    \"What is O-RAN?\",\n    \"How does Nephio work?\",\n    \"What is O2IMS?\"\n  ],\n  \"k\": 5,\n  \"include_sources\": false\n}"
                        },
                        "url": {
                            "raw": "{{base_url}}/api/v1/query/bulk",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", "query", "bulk"]
                        }
                    }
                }
            ]
        },
        {
            "name": "System",
            "item": [
                {
                    "name": "System Status",
                    "request": {
                        "method": "GET",
                        "header": [],
                        "url": {
                            "raw": "{{base_url}}/api/v1/system/status",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", "system", "status"]
                        }
                    }
                },
                {
                    "name": "System Config",
                    "request": {
                        "method": "GET",
                        "header": [],
                        "url": {
                            "raw": "{{base_url}}/api/v1/system/config",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", "system", "config"]
                        }
                    }
                },
                {
                    "name": "System Metrics",
                    "request": {
                        "method": "GET",
                        "header": [],
                        "url": {
                            "raw": "{{base_url}}/api/v1/system/metrics",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", "system", "metrics"]
                        }
                    }
                }
            ]
        }
    ]
}
```

## Error Handling

### Common Error Responses

```python
# Error handling examples in Python

def handle_api_errors(func):
    """Decorator for handling common API errors"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                print(f"Bad Request: {e.response.json().get('message')}")
            elif e.response.status_code == 401:
                print("Unauthorized: Check your API key")
            elif e.response.status_code == 429:
                print("Rate limit exceeded: Wait before retrying")
            elif e.response.status_code == 503:
                print("Service unavailable: RAG system not ready")
            else:
                print(f"HTTP Error {e.response.status_code}: {e.response.text}")
        except requests.exceptions.Timeout:
            print("Request timeout: Try increasing timeout or check network")
        except requests.exceptions.ConnectionError:
            print("Connection error: Check if API server is running")
        except Exception as e:
            print(f"Unexpected error: {e}")
    return wrapper

@handle_api_errors
def safe_query(client, question):
    return client.query(question)
```

### Retry Logic

```python
import time
import random
from functools import wraps

def retry_with_backoff(max_retries=3, base_delay=1, max_delay=60):
    """Retry decorator with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.RequestException as e:
                    if attempt == max_retries:
                        raise e

                    # Calculate delay with jitter
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    jitter = random.uniform(0, 0.1) * delay
                    time.sleep(delay + jitter)

                    print(f"Retry {attempt + 1}/{max_retries} after {delay:.1f}s")
        return wrapper
    return decorator

@retry_with_backoff(max_retries=3)
def robust_query(client, question):
    return client.query(question)
```

## Best Practices

### 1. Rate Limiting Compliance

```python
import time
from collections import defaultdict

class RateLimitedClient:
    def __init__(self, client):
        self.client = client
        self.last_request_time = defaultdict(float)
        self.rate_limits = {
            'query': 60 / 10,      # 10 requests per minute
            'search': 60 / 20,     # 20 requests per minute
            'bulk': 60 / 2,        # 2 requests per minute
        }

    def _wait_if_needed(self, endpoint_type):
        now = time.time()
        last_time = self.last_request_time[endpoint_type]
        min_interval = self.rate_limits[endpoint_type]

        time_since_last = now - last_time
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            time.sleep(sleep_time)

        self.last_request_time[endpoint_type] = time.time()

    def query(self, question, **kwargs):
        self._wait_if_needed('query')
        return self.client.query(question, **kwargs)
```

### 2. Connection Pooling

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_robust_client(base_url, api_key=None):
    """Create a robust HTTP client with connection pooling and retries"""
    session = requests.Session()

    # Configure retries
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        backoff_factor=1,
        allowed_methods=["HEAD", "GET", "POST"]
    )

    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=10,
        pool_maxsize=20
    )

    session.mount("http://", adapter)
    session.mount("https://", adapter)

    # Set headers
    session.headers.update({
        "Content-Type": "application/json",
        "User-Agent": "oran-nephio-client/1.0.0"
    })

    if api_key:
        session.headers["Authorization"] = f"Bearer {api_key}"

    return session
```

### 3. Response Caching

```python
import hashlib
import json
import time
from typing import Dict, Optional

class CachedClient:
    def __init__(self, client, cache_ttl=300):  # 5 minutes
        self.client = client
        self.cache = {}
        self.cache_ttl = cache_ttl

    def _cache_key(self, method, *args, **kwargs):
        """Generate cache key from method and parameters"""
        key_data = f"{method}:{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _get_cached(self, key):
        """Get cached response if valid"""
        if key in self.cache:
            cached_time, cached_response = self.cache[key]
            if time.time() - cached_time < self.cache_ttl:
                return cached_response
        return None

    def _set_cache(self, key, response):
        """Cache response"""
        self.cache[key] = (time.time(), response)

    def query(self, question, **kwargs):
        # Only cache simple queries
        if not kwargs.get('stream', False):
            cache_key = self._cache_key('query', question, **kwargs)
            cached = self._get_cached(cache_key)
            if cached:
                return cached

        response = self.client.query(question, **kwargs)

        if not kwargs.get('stream', False):
            self._set_cache(cache_key, response)

        return response
```

This comprehensive integration guide provides examples for multiple programming languages and tools, making it easy for developers to integrate with the O-RAN × Nephio RAG API in their preferred environment.