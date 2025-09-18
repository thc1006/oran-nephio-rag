# O-RAN Specific Query Examples

This guide provides comprehensive examples of O-RAN specific queries that demonstrate the system's capabilities for answering questions about Open Radio Access Network architecture, components, and implementations.

## Table of Contents

- [O-RAN Architecture Queries](#o-ran-architecture-queries)
- [O-RAN Components and Interfaces](#o-ran-components-and-interfaces)
- [O-RAN Implementation Queries](#o-ran-implementation-queries)
- [O-RAN Standards and Specifications](#o-ran-standards-and-specifications)
- [O-RAN Integration with 5G/6G](#o-ran-integration-with-5g6g)
- [O-RAN Security and Management](#o-ran-security-and-management)
- [Advanced O-RAN Scenarios](#advanced-o-ran-scenarios)

## O-RAN Architecture Queries

### Basic Architecture Questions

```bash
# What is O-RAN?
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is O-RAN and how does it differ from traditional RAN?",
    "k": 8,
    "include_sources": true
  }'

# O-RAN principles
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the main principles and objectives of O-RAN architecture?",
    "k": 6,
    "include_sources": true
  }'

# O-RAN benefits
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the key benefits of implementing O-RAN compared to proprietary RAN solutions?",
    "k": 7,
    "include_sources": true
  }'
```

### Architecture Components

```bash
# O-RAN functional split
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain the O-RAN functional split and its different options (Split 7.2x, Split 8, etc.)",
    "k": 10,
    "include_sources": true,
    "context_length": 6000
  }'

# O-RAN network elements
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the main network elements in O-RAN architecture (O-DU, O-CU, O-RU)?",
    "k": 8,
    "include_sources": true
  }'

# O-RAN cloud architecture
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How does O-RAN enable cloud-native RAN deployment and what are the cloud infrastructure requirements?",
    "k": 9,
    "include_sources": true
  }'
```

## O-RAN Components and Interfaces

### O-RAN Distributed Unit (O-DU)

```bash
# O-DU functionality
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the role and functionality of the O-RAN Distributed Unit (O-DU)?",
    "k": 7,
    "include_sources": true
  }'

# O-DU interfaces
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the key interfaces connected to O-DU and their protocols (F1-U, F1-C, fronthaul)?",
    "k": 8,
    "include_sources": true
  }'

# O-DU deployment
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How can O-DU be deployed in edge computing environments and what are the hardware requirements?",
    "k": 6,
    "include_sources": true
  }'
```

### O-RAN Centralized Unit (O-CU)

```bash
# O-CU functions
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the main functions of O-RAN Centralized Unit (O-CU) and how is it split into O-CU-CP and O-CU-UP?",
    "k": 9,
    "include_sources": true
  }'

# O-CU scaling
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How does O-CU support horizontal scaling and load balancing in large O-RAN deployments?",
    "k": 7,
    "include_sources": true
  }'
```

### O-RAN Radio Unit (O-RU)

```bash
# O-RU characteristics
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the characteristics and requirements of O-RAN Radio Unit (O-RU)?",
    "k": 6,
    "include_sources": true
  }'

# O-RU fronthaul
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How does the fronthaul interface work between O-DU and O-RU using eCPRI?",
    "k": 8,
    "include_sources": true
  }'
```

### O-RAN Interfaces and Protocols

```bash
# E2 interface
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the E2 interface in O-RAN and how does it enable near-real-time RIC functionality?",
    "k": 8,
    "include_sources": true
  }'

# A1 interface
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain the A1 interface and its role in policy management between Non-RT RIC and Near-RT RIC",
    "k": 7,
    "include_sources": true
  }'

# O1 interface
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the O1 interface and how does it support O&M (Operations and Maintenance) in O-RAN?",
    "k": 6,
    "include_sources": true
  }'
```

## O-RAN Implementation Queries

### RAN Intelligent Controller (RIC)

```bash
# Near-RT RIC
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the Near-Real-Time RIC and what types of applications (xApps) can run on it?",
    "k": 9,
    "include_sources": true,
    "context_length": 7000
  }'

# Non-RT RIC
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How does the Non-Real-Time RIC complement Near-RT RIC and what are rApps?",
    "k": 7,
    "include_sources": true
  }'

# RIC deployment
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How can RIC components be deployed in Kubernetes environments and integrated with cloud platforms?",
    "k": 8,
    "include_sources": true
  }'
```

### O-RAN Software Community (OSC)

```bash
# OSC projects
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the main projects and components developed by O-RAN Software Community (OSC)?",
    "k": 10,
    "include_sources": true
  }'

# OSC integration
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do OSC reference implementations integrate with commercial O-RAN deployments?",
    "k": 7,
    "include_sources": true
  }'
```

### Virtualization and Containerization

```bash
# O-RAN virtualization
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How are O-RAN network functions virtualized and what are the performance considerations?",
    "k": 8,
    "include_sources": true
  }'

# Container deployment
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the best practices for deploying O-RAN functions in containers and Kubernetes?",
    "k": 9,
    "include_sources": true
  }'
```

## O-RAN Standards and Specifications

### O-RAN Alliance Specifications

```bash
# O-RAN specifications overview
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the key technical specifications published by O-RAN Alliance and their scope?",
    "k": 10,
    "include_sources": true,
    "context_length": 8000
  }'

# O-RAN conformance testing
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How does O-RAN conformance testing work and what are the certification requirements?",
    "k": 7,
    "include_sources": true
  }'
```

### Standards Compliance

```bash
# 3GPP integration
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How does O-RAN align with 3GPP standards and what are the key integration points?",
    "k": 8,
    "include_sources": true
  }'

# ORAN vs 3GPP
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the differences and complementary aspects between O-RAN and 3GPP specifications?",
    "k": 6,
    "include_sources": true
  }'
```

## O-RAN Integration with 5G/6G

### 5G Integration

```bash
# O-RAN in 5G networks
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How does O-RAN integrate with 5G core network and what are the deployment scenarios?",
    "k": 9,
    "include_sources": true
  }'

# Network slicing
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How does O-RAN support 5G network slicing and dynamic slice management?",
    "k": 8,
    "include_sources": true
  }'

# Edge computing
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the role of O-RAN in enabling 5G edge computing and MEC (Multi-access Edge Computing)?",
    "k": 7,
    "include_sources": true
  }'
```

### 6G Evolution

```bash
# O-RAN and 6G
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How is O-RAN architecture evolving to support future 6G requirements and use cases?",
    "k": 8,
    "include_sources": true
  }'

# AI/ML integration
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How does O-RAN enable AI/ML integration in RAN optimization and what are the use cases?",
    "k": 10,
    "include_sources": true,
    "context_length": 7000
  }'
```

## O-RAN Security and Management

### Security Architecture

```bash
# O-RAN security
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the security considerations and threat models for O-RAN deployments?",
    "k": 9,
    "include_sources": true
  }'

# Zero-trust security
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How can zero-trust security principles be applied to O-RAN network architecture?",
    "k": 7,
    "include_sources": true
  }'
```

### Network Management

```bash
# O-RAN orchestration
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How does O-RAN support automated network orchestration and lifecycle management?",
    "k": 8,
    "include_sources": true
  }'

# Performance monitoring
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the key performance indicators (KPIs) and monitoring capabilities in O-RAN?",
    "k": 7,
    "include_sources": true
  }'
```

## Advanced O-RAN Scenarios

### Multi-vendor Integration

```bash
# Multi-vendor scenarios
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How does O-RAN enable multi-vendor interoperability and what are the integration challenges?",
    "k": 10,
    "include_sources": true,
    "context_length": 8000
  }'

# Vendor ecosystem
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the current O-RAN vendor ecosystem and how can operators build diverse supply chains?",
    "k": 8,
    "include_sources": true
  }'
```

### Use Case Specific Queries

```bash
# Private networks
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How can O-RAN be deployed for private 5G networks in enterprise and industrial scenarios?",
    "k": 9,
    "include_sources": true
  }'

# Rural connectivity
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the benefits of O-RAN for rural and remote area connectivity solutions?",
    "k": 6,
    "include_sources": true
  }'

# Massive IoT
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How does O-RAN support massive IoT deployments and what are the optimization strategies?",
    "k": 7,
    "include_sources": true
  }'
```

### Testing and Validation

```bash
# O-RAN testing
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the testing methodologies and validation procedures for O-RAN implementations?",
    "k": 8,
    "include_sources": true
  }'

# Interoperability testing
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How is interoperability testing conducted between different O-RAN vendors and components?",
    "k": 7,
    "include_sources": true
  }'
```

## Python Examples for O-RAN Queries

```python
import requests
import json

class ORANQueryExamples:
    def __init__(self, base_url="http://localhost:8000", api_key=None):
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    def query_oran_architecture(self):
        """Query O-RAN architecture basics"""
        questions = [
            "What is O-RAN and how does it differ from traditional RAN?",
            "What are the main components of O-RAN architecture?",
            "How does O-RAN enable vendor diversity and interoperability?"
        ]

        results = []
        for question in questions:
            response = requests.post(
                f"{self.base_url}/api/v1/query",
                headers=self.headers,
                json={
                    "query": question,
                    "k": 8,
                    "include_sources": True
                }
            )
            results.append(response.json())

        return results

    def query_oran_components(self):
        """Query specific O-RAN components"""
        component_queries = {
            "O-DU": "What is the role and functionality of O-RAN Distributed Unit (O-DU)?",
            "O-CU": "Explain O-RAN Centralized Unit (O-CU) and its split into CP and UP",
            "O-RU": "What are the characteristics of O-RAN Radio Unit (O-RU)?",
            "RIC": "What is RAN Intelligent Controller and how does it work?"
        }

        results = {}
        for component, question in component_queries.items():
            response = requests.post(
                f"{self.base_url}/api/v1/query",
                headers=self.headers,
                json={
                    "query": question,
                    "k": 6,
                    "include_sources": True
                }
            )
            results[component] = response.json()

        return results

    def search_oran_topics(self, topics):
        """Search for specific O-RAN topics"""
        results = {}

        for topic in topics:
            response = requests.post(
                f"{self.base_url}/api/v1/query/search",
                headers=self.headers,
                json={
                    "query": topic,
                    "k": 10,
                    "score_threshold": 0.7
                }
            )
            results[topic] = response.json()

        return results

    def bulk_oran_queries(self):
        """Process multiple O-RAN queries in bulk"""
        questions = [
            "What is E2 interface in O-RAN?",
            "How does A1 interface work?",
            "What is O1 interface used for?",
            "How does O-RAN support network slicing?",
            "What are xApps in Near-RT RIC?"
        ]

        response = requests.post(
            f"{self.base_url}/api/v1/query/bulk",
            headers=self.headers,
            json={
                "queries": questions,
                "k": 5,
                "include_sources": False
            }
        )

        return response.json()

# Example usage
if __name__ == "__main__":
    oran_client = ORANQueryExamples()

    # Query architecture
    print("=== O-RAN Architecture ===")
    arch_results = oran_client.query_oran_architecture()
    for result in arch_results:
        print(f"Q: {result.get('query', 'Unknown')}")
        print(f"A: {result['answer'][:200]}...")
        print()

    # Query components
    print("=== O-RAN Components ===")
    comp_results = oran_client.query_oran_components()
    for component, result in comp_results.items():
        print(f"{component}: {result['answer'][:150]}...")
        print()

    # Search topics
    print("=== Topic Search ===")
    topics = ["fronthaul", "eCPRI", "network slicing", "xApps"]
    search_results = oran_client.search_oran_topics(topics)
    for topic, result in search_results.items():
        print(f"{topic}: {result['total_found']} documents found")

    # Bulk queries
    print("=== Bulk Queries ===")
    bulk_results = oran_client.bulk_oran_queries()
    for i, result in enumerate(bulk_results['results']):
        print(f"A{i+1}: {result['answer'][:100]}...")
```

This comprehensive set of O-RAN specific queries demonstrates the system's capability to answer detailed questions about Open RAN architecture, components, implementations, and integration scenarios. The examples cover everything from basic concepts to advanced deployment scenarios, making it valuable for telecom engineers, network architects, and system integrators working with O-RAN technologies.