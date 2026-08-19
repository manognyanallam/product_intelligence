# Product Intelligence Platform — Architecture Document

## UniHack by Unilog — AI-Powered Product Intelligence

---

## 1. System Overview

The Product Intelligence Platform transforms raw, minimal product data (Manufacturer Part Number, Brand, Short Description) into rich, structured, validated, commerce-ready product intelligence. It leverages a **Multi-Agent AI Pipeline** powered by **Google Gemini**, **LangChain**, and **ChromaDB** for retrieval-augmented generation (RAG), with a **React** frontend and **FastAPI** backend.

### Core Capabilities

| Capability | Description |
|---|---|
| **Product Ingestion** | Accept MPN, Brand, Short Description |
| **Intelligence Retrieval** | Web-enhanced product information lookup |
| **Structured Generation** | AI-powered enrichment of product attributes |
| **Validation** | Cross-check generated data against sources |
| **Confidence Scoring** | Quantify reliability of each attribute |
| **Source Attribution** | Track and display provenance of each data point |
| **JSON Export** | Download structured product intelligence |

---

## 2. Folder Structure

```
product-intelligence-platform/
│
├── frontend/                          # React Application
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── Layout/
│   │   │   │   ├── Header.jsx
│   │   │   │   ├── Sidebar.jsx
│   │   │   │   └── Footer.jsx
│   │   │   ├── ProductInput/
│   │   │   │   ├── ProductForm.jsx
│   │   │   │   └── ProductForm.css
│   │   │   ├── IntelligenceView/
│   │   │   │   ├── IntelligenceCard.jsx
│   │   │   │   ├── AttributeTable.jsx
│   │   │   │   ├── ConfidenceBadge.jsx
│   │   │   │   └── SourceIndicator.jsx
│   │   │   ├── ValidationPanel/
│   │   │   │   ├── ValidationReport.jsx
│   │   │   │   └── ValidationTimeline.jsx
│   │   │   ├── Timeline/
│   │   │   │   └── AgentTimeline.jsx
│   │   │   └── Export/
│   │   │       └── ExportButton.jsx
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── ProductDetail.jsx
│   │   │   └── History.jsx
│   │   ├── hooks/
│   │   │   ├── useProductIntelligence.js
│   │   │   └── useExport.js
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── context/
│   │   │   └── ProductContext.jsx
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── index.js
│   ├── package.json
│   └── .env
│
├── backend/                           # FastAPI Application
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI entry point, middleware, CORS
│   │   ├── config.py                  # Environment config, settings
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── product.py         # /api/products endpoints
│   │   │   │   ├── intelligence.py    # /api/intelligence endpoints
│   │   │   │   ├── export.py          # /api/export endpoints
│   │   │   │   └── health.py          # /api/health endpoint
│   │   │   └── dependencies.py        # Dependency injection
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── domain/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── product.py         # Product domain models
│   │   │   │   ├── intelligence.py    # Intelligence models
│   │   │   │   └── validation.py      # Validation models
│   │   │   └── schemas/
│   │   │       ├── __init__.py
│   │   │       ├── request.py         # API request schemas (Pydantic)
│   │   │       └── response.py        # API response schemas (Pydantic)
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── product_service.py     # Orchestrates product intelligence
│   │   │   ├── vector_service.py      # ChromaDB operations
│   │   │   └── export_service.py      # JSON export logic
│   │   │
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── orchestrator.py        # Multi-agent orchestrator
│   │   │   ├── base_agent.py          # Abstract base agent class
│   │   │   ├── retrieval_agent.py     # Agent: Retrieve product info
│   │   │   ├── enrichment_agent.py    # Agent: Enrich & generate attributes
│   │   │   ├── validation_agent.py    # Agent: Validate generated data
│   │   │   ├── confidence_agent.py    # Agent: Compute confidence scores
│   │   │   └── sourcing_agent.py      # Agent: Track & attribute sources
│   │   │
│   │   ├── pipeline/
│   │   │   ├── __init__.py
│   │   │   ├── rag_pipeline.py        # Retrieval-Augmented Generation
│   │   │   ├── prompt_templates.py    # LangChain prompt templates
│   │   │   ├── chain_builder.py       # LangChain chain construction
│   │   │   └── gemini_client.py       # Gemini API wrapper
│   │   │
│   │   ├── rag/
│   │   │   ├── __init__.py
│   │   │   ├── vector_store.py        # ChromaDB client & operations
│   │   │   ├── embeddings.py          # Embedding generation
│   │   │   ├── retriever.py           # Retrieval strategies
│   │   │   └── document_loader.py     # Load & chunk documents
│   │   │
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── chroma_client.py       # ChromaDB connection management
│   │   │   └── seed_data.py           # Initial product catalog seed
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── logger.py              # Structured logging
│   │       ├── metrics.py             # Performance metrics
│   │       └── helpers.py             # Utility functions
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_agents/
│   │   ├── test_pipeline/
│   │   ├── test_api/
│   │   └── test_rag/
│   │
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
│
├── docker-compose.yml                 # Multi-service orchestration
├── .gitignore
└── README.md
```

---

## 3. Data Flow Architecture

### 3.1 End-to-End Data Flow

```
┌──────────────┐     ┌──────────────────┐     ┌───────────────────┐
│  User Input  │────▶│  FastAPI Backend  │────▶│  Multi-Agent      │
│  (MPN, Brand,│     │  (REST API)       │     │  Orchestrator     │
│   Desc)      │     └──────────────────┘     └────────┬──────────┘
└──────────────┘                                       │
                                                       ▼
                                              ┌───────────────────┐
                                              │  AI Pipeline      │
                                              │  ┌─────────────┐  │
                                              │  │Retrieval    │  │
                                              │  │Agent        │  │
                                              │  └──────┬──────┘  │
                                              │         ▼         │
                                              │  ┌─────────────┐  │
                                              │  │Enrichment   │  │
                                              │  │Agent        │  │
                                              │  └──────┬──────┘  │
                                              │         ▼         │
                                              │  ┌─────────────┐  │
                                              │  │Validation   │  │
                                              │  │Agent        │  │
                                              │  └──────┬──────┘  │
                                              │         ▼         │
                                              │  ┌─────────────┐  │
                                              │  │Confidence   │  │
                                              │  │Agent        │  │
                                              │  └──────┬──────┘  │
                                              │         ▼         │
                                              │  ┌─────────────┐  │
                                              │  │Sourcing     │  │
                                              │  │Agent        │  │
                                              │  └─────────────┘  │
                                              └───────────────────┘
                                                       │
                                                       ▼
                                              ┌───────────────────┐
                                              │  ChromaDB         │
                                              │  (Vector Store)   │
                                              └───────────────────┘
                                                       │
                                                       ▼
                                              ┌───────────────────┐
                                              │  RAG Pipeline     │
                                              │  (Retrieve +      │
                                              │   Generate)       │
                                              └───────────────────┘
                                                       │
                                                       ▼
                                              ┌───────────────────┐
                                              │  Response         │
                                              │  (JSON: enriched  │
                                              │   product, scores,│
                                              │   sources, valid.)│
                                              └───────────────────┘
```

### 3.2 Detailed Data Flow Steps

| Step | Component | Action | Data |
|---|---|---|---|
| 1 | **React Frontend** | User submits form | `{ mpn, brand, description }` |
| 2 | **FastAPI Route** | Validate input, dispatch to orchestrator | `ProductRequest` |
| 3 | **Orchestrator** | Create agent context, initiate pipeline | `AgentContext` |
| 4 | **Retrieval Agent** | Query ChromaDB + Gemini for similar products | `RetrievedDocuments` |
| 5 | **RAG Pipeline** | Embed query, retrieve top-k, augment prompt | `ContextualizedPrompt` |
| 6 | **Enrichment Agent** | Gemini generates structured attributes | `RawEnrichedProduct` |
| 7 | **Validation Agent** | Cross-check attributes against sources | `ValidationReport` |
| 8 | **Confidence Agent** | Score each attribute (0.0–1.0) | `ConfidenceScores` |
| 9 | **Sourcing Agent** | Trace each attribute to its source | `SourceAttributions` |
| 10 | **Vector Service** | Store enriched product in ChromaDB | `VectorStore` |
| 11 | **FastAPI Response** | Return complete intelligence payload | `ProductIntelligenceResponse` |
| 12 | **React Frontend** | Render cards, badges, timeline | UI Components |

---

## 4. API Endpoints

### 4.1 RESTful API Design

| Method | Endpoint | Description | Request Body | Response |
|---|---|---|---|---|
| `POST` | `/api/v1/products/intelligence` | Generate product intelligence | `ProductRequest` | `ProductIntelligenceResponse` |
| `GET` | `/api/v1/products/{product_id}` | Get product by ID | — | `ProductIntelligenceResponse` |
| `GET` | `/api/v1/products` | List all products | Query params (page, limit) | `PaginatedProducts` |
| `GET` | `/api/v1/products/search?q=` | Search products | Query params | `PaginatedProducts` |
| `POST` | `/api/v1/export/{product_id}` | Export product as JSON | — | JSON file download |
| `POST` | `/api/v1/export/batch` | Batch export products | `{ product_ids: [] }` | JSON file download |
| `GET` | `/api/v1/health` | Health check | — | `{ status, version }` |

### 4.2 Request/Response Schemas

**POST /api/v1/products/intelligence**

```json
// Request
{
  "mpn": "SN74LS00N",
  "brand": "Texas Instruments",
  "description": "Quad 2-input NAND gate",
  "options": {
    "include_web_search": true,
    "confidence_threshold": 0.7
  }
}

// Response
{
  "product_id": "prod_abc123",
  "status": "completed",
  "input": {
    "mpn": "SN74LS00N",
    "brand": "Texas Instruments",
    "description": "Quad 2-input NAND gate"
  },
  "enriched_data": {
    "mpn": "SN74LS00N",
    "brand": "Texas Instruments",
    "manufacturer": "Texas Instruments",
    "category": "Integrated Circuits > Logic Gates",
    "description": "Quad 2-Input Positive-NAND Gate",
    "long_description": "The SN74LS00N contains four independent 2-input NAND gates...",
    "specifications": {
      "technology": "LS (Low-Power Schottky)",
      "supply_voltage_min": "4.75V",
      "supply_voltage_max": "5.25V",
      "operating_temp_min": "0°C",
      "operating_temp_max": "70°C",
      "propagation_delay": "15ns",
      "package_type": "PDIP-14",
      "logic_family": "74LS",
      "number_of_gates": 4,
      "inputs_per_gate": 2
    },
    "compliance": ["RoHS", "REACH"],
    "alternate_parts": ["SN74LS00N", "MC74LS00N", "DM74LS00N"],
    "datasheet_url": "https://www.ti.com/lit/ds/symlink/sn74ls00.pdf"
  },
  "confidence_scores": {
    "overall": 0.94,
    "attributes": {
      "mpn": 1.0,
      "brand": 1.0,
      "category": 0.92,
      "description": 0.95,
      "specifications": 0.88,
      "compliance": 0.85,
      "alternate_parts": 0.78
    }
  },
  "validation": {
    "status": "passed",
    "checks": [
      {
        "attribute": "mpn",
        "status": "verified",
        "message": "MPN matches manufacturer database"
      },
      {
        "attribute": "specifications",
        "status": "partial",
        "message": "3 of 5 specs verified against datasheet",
        "details": {
          "verified": ["supply_voltage_min", "supply_voltage_max", "package_type"],
          "unverified": ["propagation_delay", "operating_temp_min"]
        }
      }
    ],
    "issues": []
  },
  "sources": [
    {
      "source_id": "src_001",
      "type": "datasheet",
      "name": "TI SN74LS00N Datasheet",
      "url": "https://www.ti.com/lit/ds/symlink/sn74ls00.pdf",
      "attributes_used": ["specifications", "description"],
      "relevance_score": 0.98
    },
    {
      "source_id": "src_002",
      "type": "vector_db",
      "name": "Product Catalog (ChromaDB)",
      "collection": "product_catalog",
      "attributes_used": ["category", "alternate_parts"],
      "relevance_score": 0.85
    },
    {
      "source_id": "src_003",
      "type": "knowledge_base",
      "name": "Gemini Knowledge Base",
      "attributes_used": ["compliance", "long_description"],
      "relevance_score": 0.76
    }
  ],
  "agent_timeline": [
    { "agent": "retrieval", "started_at": "...", "completed_at": "...", "duration_ms": 320 },
    { "agent": "enrichment", "started_at": "...", "completed_at": "...", "duration_ms": 1450 },
    { "agent": "validation", "started_at": "...", "completed_at": "...", "duration_ms": 210 },
    { "agent": "confidence", "started_at": "...", "completed_at": "...", "duration_ms": 95 },
    { "agent": "sourcing", "started_at": "...", "completed_at": "...", "duration_ms": 110 }
  ],
  "metadata": {
    "model": "gemini-2.0-flash",
    "processing_time_ms": 2185,
    "rag_iterations": 2,
    "vectors_retrieved": 5
  },
  "created_at": "2025-01-15T10:30:00Z"
}
```

---

## 5. Database Design (ChromaDB)

### 5.1 Collections Schema

ChromaDB is a vector database. We use **3 collections** for different purposes.

#### Collection 1: `product_catalog`

| Field | Type | Description |
|---|---|---|
| `id` | `string` | Unique product ID |
| `embedding` | `float[]` | 768-dim embedding (text-embedding-004) |
| `metadata.mpn` | `string` | Manufacturer Part Number |
| `metadata.brand` | `string` | Brand name |
| `metadata.category` | `string` | Product category hierarchy |
| `metadata.description` | `string` | Short product description |
| `metadata.enriched` | `boolean` | Whether enriched by AI |
| `metadata.timestamp` | `string` | ISO 8601 timestamp |
| `document` | `string` | Combined text: "MPN BRAND DESCRIPTION CATEGORY SPECS" |

**Purpose**: Store product catalog for similarity search during RAG retrieval.

#### Collection 2: `manufacturer_specs`

| Field | Type | Description |
|---|---|---|
| `id` | `string` | Unique spec document ID |
| `embedding` | `float[]` | 768-dim embedding |
| `metadata.mpn` | `string` | MPN reference |
| `metadata.manufacturer` | `string` | Manufacturer name |
| `metadata.spec_type` | `string` | e.g., "datasheet", "app_note" |
| `metadata.source_url` | `string` | Original source URL |
| `metadata.confidence` | `float` | Source reliability score |
| `document` | `string` | Raw specification text |

**Purpose**: Store manufacturer specifications for validation and enrichment.

#### Collection 3: `intelligence_cache`

| Field | Type | Description |
|---|---|---|
| `id` | `string` | Cache key (hash of input) |
| `embedding` | `float[]` | 768-dim embedding |
| `metadata.mpn` | `string` | MPN |
| `metadata.brand` | `string` | Brand |
| `metadata.cache_hit` | `boolean` | Whether served from cache |
| `metadata.ttl` | `string` | Expiration timestamp |
| `document` | `string` | Serialized JSON of enriched data |

**Purpose**: Cache intelligence results to avoid redundant API calls (TTL: 24h).

### 5.2 Query Patterns

| Pattern | Query | Parameters |
|---|---|---|
| **Similar product search** | `collection.query(query_embeddings=..., n_results=5)` | `n_results=5` |
| **MPN exact match** | `collection.get(where={"mpn": mpn})` | Exact filter |
| **Brand + category filter** | `collection.get(where={"$and": [{"brand": b}, {"category": c}]})` | Compound filter |
| **Semantic search** | `collection.query(query_texts=[desc], n_results=10)` | Text-to-embedding search |
| **Cache lookup** | `collection.get(where={"mpn": mpn, "brand": brand})` | Exact match cache |

---

## 6. AI Pipeline (LangChain + Gemini)

### 6.1 Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                       AI PIPELINE                                    │
│                                                                     │
│  INPUT: Raw product data (MPN, Brand, Description)                  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Stage 1: Preprocessing                                      │   │
│  │  ┌──────────┐  ┌───────────┐  ┌──────────────────────────┐  │   │
│  │  │Normalize │  │Validate   │  │Extract entities (MPN     │  │   │
│  │  │text      │──│input      │──│pattern, brand matching)  │  │   │
│  │  └──────────┘  └───────────┘  └──────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              ▼                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Stage 2: RAG Retrieval (see §7)                            │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              ▼                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Stage 3: Enrichment (Multi-Agent, see §8)                  │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              ▼                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Stage 4: Post-processing                                   │   │
│  │  ┌──────────┐  ┌───────────┐  ┌──────────────────────────┐  │   │
│  │  │Dedup     │  │Merge      │  │Format structured JSON    │  │   │
│  │  │attributes│──│sources    │──│response                  │  │   │
│  │  └──────────┘  └───────────┘  └──────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  OUTPUT: Structured ProductIntelligenceResponse                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 6.2 LangChain Components

| Component | Purpose | Implementation |
|---|---|---|
| **ChatGemini** | LLM for generation | `langchain_google_genai.ChatGoogleGenerativeAI` model: `gemini-2.0-flash` |
| **GoogleGenerativeAIEmbeddings** | Embeddings for RAG | `langchain_google_genai.GoogleGenerativeAIEmbeddings` model: `text-embedding-004` |
| **ChatPromptTemplate** | Prompt management | System + Human message templates |
| **StrOutputParser** | Output parsing | Parse LLM string output |
| **RunnableSequence** | Chain composition | Pipe operations: `prompt \| model \| parser` |
| **Chroma** | Vector store | `langchain_chroma.Chroma` |
| **BaseRetriever** | Document retrieval | Custom retriever with hybrid search |

### 6.3 Prompt Templates

**System Prompt (Enrichment Agent)**:
```
You are a Product Intelligence AI assistant. Your task is to enrich minimal
product information into a complete, structured product profile.

Given: Manufacturer Part Number (MPN), Brand, Short Description

Generate: A comprehensive product profile with:
1. Accurate category hierarchy (e.g., Electronics > Semiconductors > Logic ICs)
2. Full technical specifications table
3. Compliance and regulatory information
4. Alternate/compatible part numbers
5. A detailed, market-ready product description

Use the provided context from product databases and datasheets to ensure accuracy.
If information is not available from context, indicate low confidence rather than
hallucinating. Always cite sources for each attribute.
```

**Retrieval Prompt**:
```
Based on the product information provided, search for relevant technical
documentation, datasheets, and catalog entries. Return the most relevant
matches with their source attribution.

Product: {mpn} | {brand} | {description}
```

**Validation Prompt**:
```
Cross-check the following enriched product attributes against the provided
source documents. For each attribute, determine:
- Verified: Directly confirmed by source
- Partial: Partially supported by source
- Unverified: Cannot be confirmed from source
- Contradicted: Source contradicts the attribute

Assign a verification status and provide evidence.
```

---

## 7. RAG Pipeline (Retrieval-Augmented Generation)

### 7.1 RAG Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                         RAG PIPELINE                                 │
│                                                                      │
│  User Query: "SN74LS00N Texas Instruments Quad NAND"                │
│                                                                      │
│  ┌─────────────────┐      ┌──────────────────────────────────────┐  │
│  │ 1. Query         │      │ 2. Embedding Generation             │  │
│  │    Construction  │─────▶│    GoogleGenerativeAIEmbeddings     │  │
│  │    "MPN: SN74... │      │    text-embedding-004               │  │
│  │     Brand: TI..."│      │    768-dim vector                  │  │
│  └─────────────────┘      └────────────────┬─────────────────────┘  │
│                                            ▼                        │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ 3. Vector Search (ChromaDB)                                 │   │
│  │                                                              │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────────────┐  │   │
│  │  │product_catalog│  │manufacturer_ │  │Semantic Search    │  │   │
│  │  │(top-3)       │  │specs (top-5) │  │(top-k=5)          │  │   │
│  │  └──────┬───────┘  └──────┬───────┘  └────────┬──────────┘  │   │
│  │         └─────────────────┼───────────────────┘              │   │
│  │                           ▼                                  │   │
│  │              ┌────────────────────────┐                      │   │
│  │              │ Ranked Documents       │                      │   │
│  │              │ (fusion scoring)       │                      │   │
│  │              └───────────┬────────────┘                      │   │
│  └──────────────────────────┼───────────────────────────────────┘   │
│                             ▼                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ 4. Context Assembly                                         │   │
│  │                                                              │   │
│  │  ┌──────────────────────────────────────────────────────┐    │   │
│  │  │ Retrieved Documents:                                 │    │   │
│  │  │ [Doc 1] SN74LS00N Datasheet - TI (score: 0.95)      │    │   │
│  │  │   Category: Semiconductors > Logic > NAND Gates      │    │   │
│  │  │   Specs: Vcc=4.75-5.25V, Iol=8mA, tpd=15ns...    │    │   │
│  │  │ [Doc 2] SN74LS00N - Mouser Electronics (score: 0.88)│    │   │
│  │  │   Price: $0.42, Stock: 12,500, RoHS: Yes            │    │   │
│  │  │ [Doc 3] 74LS Family Logic Guide (score: 0.72)       │    │   │
│  │  │   Power consumption: 2mW/gate, Speed: 15ns...    │    │   │
│  │  └──────────────────────────────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                             ▼                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ 5. Augmented Prompt Generation                               │   │
│  │                                                              │   │
│  │  System: "You are a product intelligence agent..."           │   │
│  │  Context: [Doc 1] ... [Doc 2] ... [Doc 3] ...               │   │
│  │  Query: "Enrich product: SN74LS00N, Texas Instruments..."   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                             ▼                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ 6. Gemini Generation → Structured Output                    │   │
│  └──────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘
```

### 7.2 Retrieval Strategies

| Strategy | When Used | k | Scoring |
|---|---|---|---|
| **Semantic Search** | Primary retrieval | 10 | Cosine similarity |
| **MPN Exact Match** | Exact lookup | 1 | Exact match |
| **Brand + Category** | Filtered retrieval | 5 | Filter + similarity |
| **Hybrid (Semantic + Keyword)** | Fallback | 15 | Weighted fusion (0.7 semantic + 0.3 keyword) |
| **MMR (Maximum Marginal Relevance)** | Diverse results | 5 | Diversity + relevance |

### 7.3 RAG Enhancement Techniques

| Technique | Implementation | Benefit |
|---|---|---|
| **Query Expansion** | Generate 3 alternative queries from input | Broader coverage |
| **Hybrid Search** | Combine dense + sparse (BM25) | Better recall |
| **Re-ranking** | Cross-encoder re-ranking of top-20 | Precision improvement |
| **Contextual Compression** | LLM extracts only relevant passages | Reduced token usage |
| **Self-Query** | LLM generates structured filters | Targeted retrieval |

---

## 8. Multi-Agent Workflow

### 8.1 Agent Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                    MULTI-AGENT ORCHESTRATOR                          │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    Orchestrator Agent                          │   │
│  │  ┌────────────────────────────────────────────────────────┐   │   │
│  │  │ Responsibilities:                                      │   │   │
│  │  │ • Receive incoming request                            │   │   │
│  │  │ • Create shared AgentContext (state object)           │   │   │
│  │  │ • Sequence agent execution (sequential or conditional) │   │   │
│  │  │ • Handle errors, retries, fallbacks                   │   │   │
│  │  │ • Aggregate results into final response               │   │   │
│  │  │ • Log metrics and timeline                            │   │   │
│  │  └────────────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│     ┌────────────────────────┼────────────────────────────┐         │
│     ▼                        ▼                            ▼         │
│  ┌──────────┐          ┌──────────┐                 ┌──────────┐   │
│  │Retrieval │          │Enrichment│                 │Validation│   │
│  │ Agent    │          │ Agent    │                 │ Agent    │   │
│  ├──────────┤          ├──────────┤                 ├──────────┤   │
│  │ Gathers  │          │ Generates│                 │ Cross-   │   │
│  │ context  │─────────▶│ enriched │────────────────▶│ checks   │   │
│  │ from RAG │          │ product  │                 │ data     │   │
│  │ & sources│          │ data     │                 │          │   │
│  └──────────┘          └──────────┘                 └──────────┘   │
│                                                           │         │
│     ┌─────────────────────────────────────────────────────┘         │
│     ▼                        ▼                            ▼         │
│  ┌──────────┐          ┌──────────┐                 ┌──────────┐   │
│  │Confidence│          │ Sourcing │                 │ Export   │   │
│  │ Agent    │          │ Agent    │                 │ Agent    │   │
│  ├──────────┤          ├──────────┤                 ├──────────┤   │
│  │ Assigns  │          │ Tracks   │                 │ Formats  │   │
│  │ confidence│◀────────│ sources  │◀────────────────│ & writes │   │
│  │ scores   │          │ for each │                 │ output   │   │
│  │          │          │ attribute│                 │          │   │
│  └──────────┘          └──────────┘                 └──────────┘   │
└──────────────────────────────────────────────────────────────────────┘
```

### 8.2 Agent Specifications

#### Agent 1: Retrieval Agent

| Aspect | Detail |
|---|---|
| **Role** | Information gatherer |
| **Input** | `ProductRequest` (mpn, brand, description) |
| **Tools** | ChromaDB vector search, Gemini web search, datasheet lookup |
| **Output** | `RetrievedContext` — list of documents with relevance scores |
| **Strategy** | Parallel query: (1) Semantic search, (2) MPN exact match, (3) Brand filtered search |
| **Fallback** | If no results, expand query via Gemini-generated synonyms |
| **LLM Call** | 1 call (query expansion) + vector DB calls |

#### Agent 2: Enrichment Agent

| Aspect | Detail |
|---|---|
| **Role** | Product data generator |
| **Input** | `ProductRequest` + `RetrievedContext` |
| **Tools** | LangChain chain with Gemini, structured output parser |
| **Output** | `EnrichedProduct` — full structured product profile |
| **Strategy** | Few-shot prompting with 3 example enrichments; chain-of-thought reasoning |
| **Fallback** | Retry with temperature=0.3 if JSON parsing fails; use Pydantic output parser |
| **LLM Call** | 1–2 calls (initial + retry) |

#### Agent 3: Validation Agent

| Aspect | Detail |
|---|---|
| **Role** | Quality assurance |
| **Input** | `EnrichedProduct` + `RetrievedContext` |
| **Tools** | Gemini comparison chain, rule-based checks (regex, pattern matching) |
| **Output** | `ValidationReport` — per-attribute verification status |
| **Strategy** | For each attribute: (1) Check if present in source docs, (2) Check if contradicts source, (3) Flag unverifiable attributes |
| **Fallback** | Regex-based validation if LLM validation fails |
| **LLM Call** | 1 call (batch validation) |

#### Agent 4: Confidence Agent

| Aspect | Detail |
|---|---|
| **Role** | Reliability scorer |
| **Input** | `EnrichedProduct` + `ValidationReport` + `RetrievedContext` |
| **Tools** | Gemini scoring chain, statistical heuristic calculator |
| **Output** | `ConfidenceScores` — per-attribute and overall scores |
| **Strategy** | Score = f(source_reliability, validation_status, source_count, consistency) |
| **Formula** | `confidence = 0.4 * validation_status + 0.3 * source_reliability + 0.2 * source_count + 0.1 * consistency` |
| **LLM Call** | 1 call (for scoring ambiguous attributes) |

#### Agent 5: Sourcing Agent

| Aspect | Detail |
|---|---|
| **Role** | Provenance tracker |
| **Input** | `EnrichedProduct` + `RetrievedContext` + agent trace logs |
| **Tools** | Document chunk mapping, URL extractor, source attribution mapper |
| **Output** | `SourceAttributions` — list of sources with mapped attributes |
| **Strategy** | Trace each generated attribute back to source document chunks; map source → attributes |
| **Fallback** | Mark as "AI-generated" if no source found |
| **LLM Call** | 0 (rule-based mapping) |

### 8.3 Agent Communication Protocol

```
AgentContext (shared state object):
{
  "request_id": "uuid",
  "input": ProductRequest,
  "status": "processing",  // processing | completed | failed
  "current_agent": "retrieval",
  "agent_results": {
    "retrieval": null | RetrievedContext,
    "enrichment": null | EnrichedProduct,
    "validation": null | ValidationReport,
    "confidence": null | ConfidenceScores,
    "sourcing": null | SourceAttributions
  },
  "errors": [],
  "timeline": [],
  "metadata": {}
}
```

### 8.4 Execution Flow

```
SEQUENTIAL (default):
  Orchestrator → Retrieval Agent → Enrichment Agent → Validation Agent
  → Confidence Agent → Sourcing Agent → Orchestrator (aggregate)

PARALLEL (optimistic):
  Orchestrator → Retrieval Agent
                 ├──→ Enrichment Agent ──→ Validation Agent ──→ Confidence Agent
                 └──→ Sourcing Agent (parallel)
  Orchestrator (merge all results)

CONDITIONAL (smart):
  If validation fails → retry Enrichment Agent with stricter constraints
  If confidence < threshold → flag for human review
  If cache hit → skip pipeline, return cached result
```

---

## 9. Technology Stack Details

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| **Frontend** | React | 18.x | UI framework |
| | React Router | 6.x | Client-side routing |
| | Axios | 1.x | HTTP client |
| | Recharts | 2.x | Confidence visualization |
| | React Bootstrap / MUI | Latest | UI component library |
| **Backend** | Python | 3.11+ | Runtime |
| | FastAPI | 0.110+ | REST API framework |
| | Uvicorn | 0.27+ | ASGI server |
| | Pydantic | 2.x | Data validation |
| **AI/ML** | LangChain | 0.3+ | LLM orchestration |
| | Google Generative AI | 0.8+ | Gemini API |
| | ChromaDB | 0.5+ | Vector database |
| **Infrastructure** | Docker | Latest | Containerization |
| | Docker Compose | Latest | Multi-service orchestration |

---

## 10. Security & Performance Considerations

### Security
- API key management via environment variables (`.env`)
- Input sanitization and validation via Pydantic schemas
- Rate limiting on `/intelligence` endpoint (10 req/min per IP)
- CORS restricted to frontend origin
- No sensitive data stored in ChromaDB

### Performance
- **Caching**: Intelligence cache in ChromaDB (TTL: 24h)
- **Async processing**: FastAPI async endpoints with `asyncio`
- **Parallel agent execution**: Optimistic workflow runs sourcing in parallel
- **Streaming**: SSE for real-time agent timeline updates
- **Batch embedding**: Process multiple queries in one embedding call
- **Connection pooling**: Reuse ChromaDB and Gemini connections

### Scalability
- Stateless FastAPI → horizontal scaling
- ChromaDB can be deployed as separate service
- Agent workers can be parallelized via Celery (future enhancement)

---

## 11. Future Enhancements

| Feature | Priority | Description |
|---|---|---|
| **Web Search Integration** | High | Real-time web scraping for datasheets |
| **User Feedback Loop** | Medium | Feedback buttons to improve AI |
| **Batch Processing** | Medium | CSV/Excel upload for bulk enrichment |
| **Human-in-the-Loop** | Low | Manual review queue for low-confidence items |
| **Multi-language Support** | Low | Product descriptions in multiple languages |
| **Price Intelligence** | Medium | Real-time pricing from distributor APIs |
| **Image Recognition** | Low | Extract MPN from product images via OCR |

---

## 12. Architecture Diagram (ASCII Overview)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      PRODUCT INTELLIGENCE PLATFORM                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────────────────────────┐    ┌──────────┐  │
│  │  REACT       │    │         FASTAPI BACKEND           │    │CHROMADB  │  │
│  │  FRONTEND    │    │                                  │    │          │  │
│  │              │    │  ┌────────────────────────────┐  │    │prod_cat  │  │
│  │  ProductForm │───▶│  │  Multi-Agent Orchestrator │  │───▶│mfr_specs │  │
│  │              │    │  │                            │  │    │cache     │  │
│  │  Intell.     │    │  │  Retrieval    Enrichment   │  │    └──────────┘  │
│  │  Card        │◀───│  │  Agent        Agent        │  │          │       │
│  │              │    │  │                            │  │          ▼       │
│  │  Validation  │    │  │  Validation   Confidence   │  │  ┌──────────┐  │
│  │  Report      │◀───│  │  Agent        Agent        │  │  │ GEMINI   │  │
│  │              │    │  │                            │  │  │ API      │  │
│  │  Agent       │    │  │  Sourcing     Export       │  │  │          │  │
│  │  Timeline    │◀───│  │  Agent        Agent        │  │  │text-     │  │
│  │              │    │  └────────────────────────────┘  │  │embedding │  │
│  │  Export JSON │◀───│                                  │  │          │  │
│  └──────────────┘    └──────────────────────────────────┘  └──────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

*Document Version: 1.0.0*
*Prepared for: UniHack by Unilog*
