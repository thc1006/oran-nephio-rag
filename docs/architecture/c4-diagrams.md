# C4 Architecture Diagrams for Nephio & O-RAN RAG System

## Overview

This document provides detailed C4 model diagrams for the comprehensive RAG system architecture. The C4 model offers a hierarchical set of diagrams to visualize software architecture at different levels of abstraction.

---

## Level 1: System Context

```mermaid
graph TB
    subgraph "External Systems"
        DEV[Developers]
        DEVOPS[DevOps Engineers]
        ARCH[System Architects]
        TOOLS[Development Tools]
        GIT[Git Repositories]
        DOCS[Official Documentation]
    end

    subgraph "Nephio & O-RAN RAG System"
        RAG[RAG System]
    end

    subgraph "External Services"
        CLAUDE[Claude API]
        GITHUB[GitHub API]
        CONFLUENCE[Confluence]
        WEBSITES[Documentation Websites]
    end

    DEV --> RAG
    DEVOPS --> RAG
    ARCH --> RAG
    TOOLS --> RAG

    RAG --> CLAUDE
    RAG --> GITHUB
    RAG --> CONFLUENCE
    RAG --> WEBSITES

    GIT --> RAG
    DOCS --> RAG

    classDef person fill:#08427b,stroke:#fff,stroke-width:2px,color:#fff
    classDef system fill:#1168bd,stroke:#fff,stroke-width:2px,color:#fff
    classDef external fill:#999,stroke:#fff,stroke-width:2px,color:#fff

    class DEV,DEVOPS,ARCH person
    class RAG system
    class CLAUDE,GITHUB,CONFLUENCE,WEBSITES,GIT,DOCS external
```

### Context Description

The **Nephio & O-RAN RAG System** serves as a central knowledge hub for:

- **Developers**: Building cloud-native network functions
- **DevOps Engineers**: Deploying and managing Nephio clusters
- **System Architects**: Designing O-RAN implementations

The system integrates with external documentation sources and provides intelligent query capabilities through multiple interfaces.

---

## Level 2: Container Diagram

```mermaid
graph TB
    subgraph "Users"
        DEV[Developers]
        CLI[CLI Tools]
        IDE[IDE Extensions]
    end

    subgraph "Nephio & O-RAN RAG System"
        subgraph "Presentation Layer"
            WEB[Web UI<br/>React/TypeScript]
            API[API Gateway<br/>Kong/Envoy]
            WS[WebSocket Handler<br/>Python/FastAPI]
        end

        subgraph "Application Layer"
            RAGAPI[RAG API Service<br/>FastAPI/Python]
            QUERY[Query Processor<br/>Python]
            RETRIEVAL[Retrieval Engine<br/>Python]
            LLM[LLM Integration<br/>Python]
        end

        subgraph "Processing Layer"
            INGESTION[Document Processor<br/>Celery/Python]
            EMBED[Embedding Service<br/>Python/HuggingFace]
            MONITOR[Monitoring Service<br/>Python]
        end

        subgraph "Data Layer"
            VECTOR[Vector Database<br/>Qdrant]
            CACHE[Cache Layer<br/>Redis]
            QUEUE[Message Queue<br/>Redis/Kafka]
            STORAGE[Document Storage<br/>MinIO/S3]
        end
    end

    subgraph "External Systems"
        DOCS_EXT[External Documentation]
        CLAUDE_API[Claude API]
        METRICS[Prometheus/Grafana]
    end

    %% User interactions
    DEV --> WEB
    CLI --> API
    IDE --> API

    %% Presentation layer connections
    WEB --> API
    API --> RAGAPI
    API --> WS
    WS --> RAGAPI

    %% Application layer connections
    RAGAPI --> QUERY
    QUERY --> RETRIEVAL
    QUERY --> LLM
    RETRIEVAL --> VECTOR
    LLM --> CLAUDE_API

    %% Processing layer connections
    INGESTION --> EMBED
    INGESTION --> STORAGE
    EMBED --> VECTOR
    MONITOR --> METRICS

    %% Data layer connections
    RAGAPI --> CACHE
    INGESTION --> QUEUE
    QUERY --> CACHE

    %% External connections
    INGESTION --> DOCS_EXT

    classDef user fill:#08427b,stroke:#fff,stroke-width:2px,color:#fff
    classDef presentation fill:#1168bd,stroke:#fff,stroke-width:2px,color:#fff
    classDef application fill:#3498db,stroke:#fff,stroke-width:2px,color:#fff
    classDef processing fill:#2ecc71,stroke:#fff,stroke-width:2px,color:#fff
    classDef data fill:#e74c3c,stroke:#fff,stroke-width:2px,color:#fff
    classDef external fill:#95a5a6,stroke:#fff,stroke-width:2px,color:#fff

    class DEV,CLI,IDE user
    class WEB,API,WS presentation
    class RAGAPI,QUERY,RETRIEVAL,LLM application
    class INGESTION,EMBED,MONITOR processing
    class VECTOR,CACHE,QUEUE,STORAGE data
    class DOCS_EXT,CLAUDE_API,METRICS external
```

### Container Responsibilities

#### Presentation Layer
- **Web UI**: React-based interface for interactive queries
- **API Gateway**: Request routing, authentication, rate limiting
- **WebSocket Handler**: Real-time streaming responses

#### Application Layer
- **RAG API Service**: Main API orchestrator
- **Query Processor**: Query understanding and enhancement
- **Retrieval Engine**: Multi-stage document retrieval
- **LLM Integration**: Response generation and streaming

#### Processing Layer
- **Document Processor**: Asynchronous document ingestion
- **Embedding Service**: Vector generation for documents
- **Monitoring Service**: System health and metrics

#### Data Layer
- **Vector Database**: Semantic search and similarity matching
- **Cache Layer**: Multi-level caching for performance
- **Message Queue**: Asynchronous task processing
- **Document Storage**: Raw document and metadata storage

---

## Level 3: Component Diagram - RAG API Service

```mermaid
graph TB
    subgraph "RAG API Service Container"
        subgraph "API Controllers"
            QUERY_CTRL[Query Controller]
            DOC_CTRL[Document Controller]
            SEARCH_CTRL[Search Controller]
            FEEDBACK_CTRL[Feedback Controller]
        end

        subgraph "Core Services"
            QUERY_SVC[Query Service]
            RETRIEVAL_SVC[Retrieval Service]
            GENERATION_SVC[Generation Service]
            CACHE_SVC[Cache Service]
        end

        subgraph "Processing Components"
            QUERY_PROC[Query Processor]
            INTENT_CLASS[Intent Classifier]
            CONTEXT_BUILDER[Context Builder]
            RESPONSE_FORMATTER[Response Formatter]
        end

        subgraph "Integration Adapters"
            VECTOR_ADAPTER[Vector DB Adapter]
            LLM_ADAPTER[LLM Adapter]
            CACHE_ADAPTER[Cache Adapter]
            METRICS_ADAPTER[Metrics Adapter]
        end

        subgraph "Utilities"
            VALIDATOR[Input Validator]
            SANITIZER[Output Sanitizer]
            RATE_LIMITER[Rate Limiter]
            AUTH_HANDLER[Auth Handler]
        end
    end

    %% External dependencies
    VECTOR_DB[(Vector Database)]
    LLM_API[Claude API]
    REDIS[(Redis Cache)]
    PROMETHEUS[Prometheus]

    %% Controller to Service connections
    QUERY_CTRL --> QUERY_SVC
    DOC_CTRL --> RETRIEVAL_SVC
    SEARCH_CTRL --> RETRIEVAL_SVC
    FEEDBACK_CTRL --> CACHE_SVC

    %% Service to Processing connections
    QUERY_SVC --> QUERY_PROC
    QUERY_SVC --> INTENT_CLASS
    RETRIEVAL_SVC --> CONTEXT_BUILDER
    GENERATION_SVC --> RESPONSE_FORMATTER

    %% Processing to Adapter connections
    QUERY_PROC --> VECTOR_ADAPTER
    CONTEXT_BUILDER --> VECTOR_ADAPTER
    RESPONSE_FORMATTER --> LLM_ADAPTER
    CACHE_SVC --> CACHE_ADAPTER

    %% Adapter to External connections
    VECTOR_ADAPTER --> VECTOR_DB
    LLM_ADAPTER --> LLM_API
    CACHE_ADAPTER --> REDIS
    METRICS_ADAPTER --> PROMETHEUS

    %% Utility integrations
    VALIDATOR --> QUERY_CTRL
    SANITIZER --> RESPONSE_FORMATTER
    RATE_LIMITER --> QUERY_CTRL
    AUTH_HANDLER --> QUERY_CTRL

    classDef controller fill:#3498db,stroke:#fff,stroke-width:2px,color:#fff
    classDef service fill:#2ecc71,stroke:#fff,stroke-width:2px,color:#fff
    classDef processing fill:#f39c12,stroke:#fff,stroke-width:2px,color:#fff
    classDef adapter fill:#9b59b6,stroke:#fff,stroke-width:2px,color:#fff
    classDef utility fill:#1abc9c,stroke:#fff,stroke-width:2px,color:#fff
    classDef external fill:#95a5a6,stroke:#fff,stroke-width:2px,color:#fff

    class QUERY_CTRL,DOC_CTRL,SEARCH_CTRL,FEEDBACK_CTRL controller
    class QUERY_SVC,RETRIEVAL_SVC,GENERATION_SVC,CACHE_SVC service
    class QUERY_PROC,INTENT_CLASS,CONTEXT_BUILDER,RESPONSE_FORMATTER processing
    class VECTOR_ADAPTER,LLM_ADAPTER,CACHE_ADAPTER,METRICS_ADAPTER adapter
    class VALIDATOR,SANITIZER,RATE_LIMITER,AUTH_HANDLER utility
    class VECTOR_DB,LLM_API,REDIS,PROMETHEUS external
```

---

## Level 4: Code Diagram - Query Processing Flow

```mermaid
sequenceDiagram
    participant User
    participant API as API Gateway
    participant QueryCtrl as Query Controller
    participant QuerySvc as Query Service
    participant QueryProc as Query Processor
    participant IntentClass as Intent Classifier
    participant RetrievalSvc as Retrieval Service
    participant VectorAdapter as Vector Adapter
    participant VectorDB as Vector Database
    participant LLMAdapter as LLM Adapter
    participant Claude as Claude API
    participant ResponseFormatter as Response Formatter

    User->>API: POST /api/v2/query
    API->>QueryCtrl: Forward request
    QueryCtrl->>QuerySvc: process_query(question, filters)

    QuerySvc->>QueryProc: enhance_query(question)
    QueryProc->>QueryProc: expand_synonyms()
    QueryProc->>QueryProc: normalize_terms()
    QueryProc-->>QuerySvc: enhanced_query

    QuerySvc->>IntentClass: classify_intent(enhanced_query)
    IntentClass-->>QuerySvc: intent_type

    QuerySvc->>RetrievalSvc: retrieve_context(enhanced_query, intent_type)
    RetrievalSvc->>VectorAdapter: similarity_search(query_vector)
    VectorAdapter->>VectorDB: search(vector, filters)
    VectorDB-->>VectorAdapter: similar_documents
    VectorAdapter-->>RetrievalSvc: ranked_documents

    RetrievalSvc->>RetrievalSvc: apply_contextual_filters()
    RetrievalSvc->>RetrievalSvc: rerank_with_cross_encoder()
    RetrievalSvc-->>QuerySvc: context_documents

    QuerySvc->>LLMAdapter: generate_response(question, context)
    LLMAdapter->>LLMAdapter: prepare_prompt()
    LLMAdapter->>Claude: POST /v1/messages
    Claude-->>LLMAdapter: response_text
    LLMAdapter-->>QuerySvc: llm_response

    QuerySvc->>ResponseFormatter: format_response(response, context)
    ResponseFormatter->>ResponseFormatter: add_sources()
    ResponseFormatter->>ResponseFormatter: add_metadata()
    ResponseFormatter-->>QuerySvc: formatted_response

    QuerySvc-->>QueryCtrl: final_response
    QueryCtrl-->>API: HTTP 200 + response
    API-->>User: JSON response
```

---

## Data Flow Diagram

```mermaid
graph LR
    subgraph "Document Sources"
        GITHUB[GitHub Repositories]
        DOCS[Documentation Sites]
        PDFS[PDF Documents]
        APIS[API Specifications]
    end

    subgraph "Ingestion Pipeline"
        SCRAPER[Web Scraper]
        PARSER[Content Parser]
        CLEANER[Content Cleaner]
        CHUNKER[Document Chunker]
    end

    subgraph "Processing Pipeline"
        EMBEDDER[Embedding Generator]
        INDEXER[Vector Indexer]
        METADATA[Metadata Extractor]
        VALIDATOR[Quality Validator]
    end

    subgraph "Storage Layer"
        VECTOR_STORE[(Vector Database)]
        DOC_STORE[(Document Store)]
        METADATA_STORE[(Metadata Store)]
        CACHE_STORE[(Cache Store)]
    end

    subgraph "Query Pipeline"
        QUERY_INPUT[User Query]
        QUERY_ENHANCER[Query Enhancer]
        RETRIEVER[Document Retriever]
        RANKER[Result Ranker]
        GENERATOR[Response Generator]
        FORMATTER[Response Formatter]
    end

    %% Document ingestion flow
    GITHUB --> SCRAPER
    DOCS --> SCRAPER
    PDFS --> PARSER
    APIS --> PARSER

    SCRAPER --> PARSER
    PARSER --> CLEANER
    CLEANER --> CHUNKER

    CHUNKER --> EMBEDDER
    CHUNKER --> METADATA
    EMBEDDER --> INDEXER
    METADATA --> VALIDATOR

    INDEXER --> VECTOR_STORE
    VALIDATOR --> DOC_STORE
    METADATA --> METADATA_STORE

    %% Query processing flow
    QUERY_INPUT --> QUERY_ENHANCER
    QUERY_ENHANCER --> RETRIEVER
    RETRIEVER --> VECTOR_STORE
    VECTOR_STORE --> RANKER
    RANKER --> GENERATOR
    GENERATOR --> FORMATTER

    %% Cache interactions
    RETRIEVER --> CACHE_STORE
    CACHE_STORE --> RETRIEVER
    GENERATOR --> CACHE_STORE

    classDef source fill:#e8f4fd,stroke:#1168bd,stroke-width:2px
    classDef ingestion fill:#fff2cc,stroke:#d6b656,stroke-width:2px
    classDef processing fill:#d5e8d4,stroke:#82b366,stroke-width:2px
    classDef storage fill:#f8cecc,stroke:#b85450,stroke-width:2px
    classDef query fill:#e1d5e7,stroke:#9673a6,stroke-width:2px

    class GITHUB,DOCS,PDFS,APIS source
    class SCRAPER,PARSER,CLEANER,CHUNKER ingestion
    class EMBEDDER,INDEXER,METADATA,VALIDATOR processing
    class VECTOR_STORE,DOC_STORE,METADATA_STORE,CACHE_STORE storage
    class QUERY_INPUT,QUERY_ENHANCER,RETRIEVER,RANKER,GENERATOR,FORMATTER query
```

---

## Deployment Architecture

```mermaid
graph TB
    subgraph "Load Balancer Layer"
        LB[Load Balancer<br/>Kubernetes Ingress]
    end

    subgraph "Application Tier"
        subgraph "API Services"
            API1[RAG API Pod 1]
            API2[RAG API Pod 2]
            API3[RAG API Pod 3]
        end

        subgraph "Processing Services"
            PROC1[Document Processor Pod 1]
            PROC2[Document Processor Pod 2]
        end

        subgraph "Embedding Services"
            EMB1[Embedding Service Pod 1]
            EMB2[Embedding Service Pod 2]
        end
    end

    subgraph "Data Tier"
        subgraph "Vector Database Cluster"
            QDRANT1[Qdrant Node 1<br/>Primary]
            QDRANT2[Qdrant Node 2<br/>Replica]
            QDRANT3[Qdrant Node 3<br/>Replica]
        end

        subgraph "Cache Cluster"
            REDIS1[Redis Primary]
            REDIS2[Redis Replica 1]
            REDIS3[Redis Replica 2]
        end

        subgraph "Storage"
            S3[Object Storage<br/>MinIO/S3]
        end
    end

    subgraph "Monitoring & Observability"
        PROM[Prometheus]
        GRAFANA[Grafana]
        JAEGER[Jaeger]
        LOKI[Loki]
    end

    subgraph "External Services"
        CLAUDE_EXT[Claude API]
        GITHUB_EXT[GitHub API]
    end

    %% Load balancer connections
    LB --> API1
    LB --> API2
    LB --> API3

    %% API to processing connections
    API1 --> PROC1
    API2 --> PROC1
    API3 --> PROC2

    %% Processing to embedding connections
    PROC1 --> EMB1
    PROC2 --> EMB2

    %% Database connections
    API1 --> QDRANT1
    API2 --> QDRANT2
    API3 --> QDRANT3

    %% Cache connections
    API1 --> REDIS1
    API2 --> REDIS1
    API3 --> REDIS1

    %% Storage connections
    PROC1 --> S3
    PROC2 --> S3

    %% Monitoring connections
    API1 --> PROM
    API2 --> PROM
    API3 --> PROM
    PROC1 --> PROM
    PROC2 --> PROM

    %% External connections
    API1 --> CLAUDE_EXT
    API2 --> CLAUDE_EXT
    API3 --> CLAUDE_EXT
    PROC1 --> GITHUB_EXT
    PROC2 --> GITHUB_EXT

    classDef lb fill:#ff9999,stroke:#cc0000,stroke-width:2px,color:#fff
    classDef api fill:#99ccff,stroke:#0066cc,stroke-width:2px,color:#fff
    classDef processing fill:#99ff99,stroke:#00cc00,stroke-width:2px,color:#000
    classDef data fill:#ffcc99,stroke:#ff6600,stroke-width:2px,color:#000
    classDef monitoring fill:#cc99ff,stroke:#6600cc,stroke-width:2px,color:#fff
    classDef external fill:#cccccc,stroke:#666666,stroke-width:2px,color:#000

    class LB lb
    class API1,API2,API3 api
    class PROC1,PROC2,EMB1,EMB2 processing
    class QDRANT1,QDRANT2,QDRANT3,REDIS1,REDIS2,REDIS3,S3 data
    class PROM,GRAFANA,JAEGER,LOKI monitoring
    class CLAUDE_EXT,GITHUB_EXT external
```

---

## Security Architecture

```mermaid
graph TB
    subgraph "External Zone"
        USER[Users]
        ATTACKER[Potential Attackers]
    end

    subgraph "DMZ (Demilitarized Zone)"
        WAF[Web Application Firewall]
        LB[Load Balancer]
        API_GW[API Gateway]
    end

    subgraph "Application Zone"
        subgraph "Authentication Layer"
            OAUTH[OAuth 2.0 / OIDC]
            JWT_VALIDATOR[JWT Validator]
            RBAC[Role-Based Access Control]
        end

        subgraph "API Services"
            RAG_API[RAG API Services]
            RATE_LIMITER[Rate Limiter]
            INPUT_VALIDATOR[Input Validator]
        end
    end

    subgraph "Data Zone"
        subgraph "Encrypted Storage"
            VECTOR_DB_ENC[(Encrypted Vector DB)]
            CACHE_ENC[(Encrypted Cache)]
            STORAGE_ENC[(Encrypted Storage)]
        end

        subgraph "Key Management"
            KMS[Key Management Service]
            SECRETS[Secrets Manager]
        end
    end

    subgraph "Network Security"
        NETWORK_POLICIES[Network Policies]
        SERVICE_MESH[Service Mesh / mTLS]
        VPN[VPN Gateway]
    end

    subgraph "Monitoring & Audit"
        SECURITY_MONITOR[Security Monitoring]
        AUDIT_LOG[Audit Logging]
        SIEM[SIEM System]
    end

    %% User flow
    USER --> WAF
    WAF --> LB
    LB --> API_GW

    %% Security checks
    API_GW --> OAUTH
    OAUTH --> JWT_VALIDATOR
    JWT_VALIDATOR --> RBAC
    RBAC --> RAG_API

    %% Request processing
    RAG_API --> RATE_LIMITER
    RATE_LIMITER --> INPUT_VALIDATOR
    INPUT_VALIDATOR --> VECTOR_DB_ENC

    %% Data protection
    VECTOR_DB_ENC --> KMS
    CACHE_ENC --> KMS
    STORAGE_ENC --> SECRETS

    %% Network security
    RAG_API --> SERVICE_MESH
    SERVICE_MESH --> NETWORK_POLICIES

    %% Monitoring
    API_GW --> SECURITY_MONITOR
    RAG_API --> AUDIT_LOG
    AUDIT_LOG --> SIEM

    %% Attack prevention
    ATTACKER -.-> WAF
    WAF -.-> ATTACKER

    classDef external fill:#ffcccc,stroke:#cc0000,stroke-width:2px
    classDef dmz fill:#ffffcc,stroke:#cccc00,stroke-width:2px
    classDef auth fill:#ccffcc,stroke:#00cc00,stroke-width:2px
    classDef app fill:#ccccff,stroke:#0000cc,stroke-width:2px
    classDef data fill:#ffccff,stroke:#cc00cc,stroke-width:2px
    classDef network fill:#ccffff,stroke:#00cccc,stroke-width:2px
    classDef monitoring fill:#f0f0f0,stroke:#666666,stroke-width:2px

    class USER,ATTACKER external
    class WAF,LB,API_GW dmz
    class OAUTH,JWT_VALIDATOR,RBAC auth
    class RAG_API,RATE_LIMITER,INPUT_VALIDATOR app
    class VECTOR_DB_ENC,CACHE_ENC,STORAGE_ENC,KMS,SECRETS data
    class NETWORK_POLICIES,SERVICE_MESH,VPN network
    class SECURITY_MONITOR,AUDIT_LOG,SIEM monitoring
```

---

## Integration Patterns

```mermaid
graph TB
    subgraph "RAG System Core"
        RAG_CORE[RAG Core Engine]
    end

    subgraph "Developer Tools Integration"
        subgraph "IDEs"
            VSCODE[VS Code Extension]
            INTELLIJ[IntelliJ Plugin]
            VIM[Vim Plugin]
        end

        subgraph "CLI Tools"
            KUBECTL[kubectl plugin]
            NEPHIO_CLI[Nephio CLI]
            CURL[curl/REST]
        end

        subgraph "CI/CD Integration"
            GITHUB_ACTIONS[GitHub Actions]
            GITLAB_CI[GitLab CI]
            JENKINS[Jenkins]
            TEKTON[Tekton Pipelines]
        end
    end

    subgraph "Documentation Integration"
        GITBOOK[GitBook]
        CONFLUENCE[Confluence]
        NOTION[Notion]
        SPHINX[Sphinx]
    end

    subgraph "Monitoring Integration"
        GRAFANA_DASH[Grafana Dashboards]
        KIBANA[Kibana]
        DATADOG[Datadog]
        NEWRELIC[New Relic]
    end

    subgraph "Notification Integration"
        SLACK[Slack Bot]
        TEAMS[Microsoft Teams]
        DISCORD[Discord Bot]
        EMAIL[Email Alerts]
    end

    %% IDE integrations
    VSCODE --> RAG_CORE
    INTELLIJ --> RAG_CORE
    VIM --> RAG_CORE

    %% CLI integrations
    KUBECTL --> RAG_CORE
    NEPHIO_CLI --> RAG_CORE
    CURL --> RAG_CORE

    %% CI/CD integrations
    GITHUB_ACTIONS --> RAG_CORE
    GITLAB_CI --> RAG_CORE
    JENKINS --> RAG_CORE
    TEKTON --> RAG_CORE

    %% Documentation integrations
    GITBOOK --> RAG_CORE
    CONFLUENCE --> RAG_CORE
    NOTION --> RAG_CORE
    SPHINX --> RAG_CORE

    %% Monitoring integrations
    RAG_CORE --> GRAFANA_DASH
    RAG_CORE --> KIBANA
    RAG_CORE --> DATADOG
    RAG_CORE --> NEWRELIC

    %% Notification integrations
    RAG_CORE --> SLACK
    RAG_CORE --> TEAMS
    RAG_CORE --> DISCORD
    RAG_CORE --> EMAIL

    classDef core fill:#ff6b6b,stroke:#ee5a52,stroke-width:3px,color:#fff
    classDef ide fill:#4ecdc4,stroke:#45b7aa,stroke-width:2px,color:#fff
    classDef cli fill:#45b7d1,stroke:#3a9bc1,stroke-width:2px,color:#fff
    classDef cicd fill:#96ceb4,stroke:#85b89d,stroke-width:2px,color:#000
    classDef docs fill:#feca57,stroke:#ff9f43,stroke-width:2px,color:#000
    classDef monitor fill:#ff9ff3,stroke:#f368e0,stroke-width:2px,color:#000
    classDef notify fill:#54a0ff,stroke:#2e86de,stroke-width:2px,color:#fff

    class RAG_CORE core
    class VSCODE,INTELLIJ,VIM ide
    class KUBECTL,NEPHIO_CLI,CURL cli
    class GITHUB_ACTIONS,GITLAB_CI,JENKINS,TEKTON cicd
    class GITBOOK,CONFLUENCE,NOTION,SPHINX docs
    class GRAFANA_DASH,KIBANA,DATADOG,NEWRELIC monitor
    class SLACK,TEAMS,DISCORD,EMAIL notify
```

---

## Summary

These C4 architecture diagrams provide a comprehensive view of the Nephio & O-RAN RAG system at multiple levels of detail:

1. **System Context**: Shows the system's place in the broader ecosystem
2. **Container Diagram**: Illustrates the high-level technical building blocks
3. **Component Diagram**: Details the internal structure of key containers
4. **Code Diagram**: Demonstrates runtime behavior and interactions

The diagrams emphasize:

- **Modularity**: Clear separation of concerns across layers
- **Scalability**: Horizontal scaling capabilities at each tier
- **Security**: Defense-in-depth approach with multiple security layers
- **Integration**: Extensive integration points for developer workflows
- **Observability**: Comprehensive monitoring and audit capabilities

This architecture supports the evolving needs of Nephio and O-RAN development teams while providing a robust foundation for future enhancements.