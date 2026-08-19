# AI Product Intelligence Platform

## Architecture Document — UniHack by Unilog

---

**Author:** Principal AI Solutions Architect  
**Version:** 2.0.0  
**Date:** January 2025  
**Event:** UniHack by Unilog Hackathon  

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [System Architecture Overview](#3-system-architecture-overview)
4. [Technology Stack](#4-technology-stack)
5. [Multi-Agent Design](#5-multi-agent-design)
6. [RAG Pipeline](#6-rag-pipeline)
7. [Database Design](#7-database-design)
8. [API Design](#8-api-design)
9. [Frontend Design](#9-frontend-design)
10. [Dashboard Components](#10-dashboard-components)
11. [Workflow](#11-workflow)
12. [Security Architecture](#12-security-architecture)
13. [Performance Considerations](#13-performance-considerations)
14. [Deployment Architecture](#14-deployment-architecture)
15. [Future Features](#15-future-features)
16. [Conclusion](#16-conclusion)

---

## 1. Executive Summary

The **AI Product Intelligence Platform** is an enterprise-grade system that transforms minimal product data — a Manufacturer Part Number (MPN), Brand, and Short Description — into rich, structured, validated, commerce-ready product intelligence. Built for the UniHack by Unilog hackathon, this architecture demonstrates advanced AI engineering using a **three-agent orchestration system**, **Retrieval-Augmented Generation (RAG)** with **ChromaDB**, and **Google Gemini** via **LangChain**. The system is designed to be practical for a 48-hour hackathon while showcasing production-grade architectural patterns used in industrial commerce.

---

## 2. Problem Statement

Manufacturers and distributors in the industrial commerce ecosystem frequently provide only skeletal product information:

| Input Field | Example |
|---|---|
| **Manufacturer Part Number** | SN74LS00N |
| **Brand** | Texas Instruments |
| **Short Description** | Quad 2-input NAND gate |

This minimal data is insufficient for modern e-commerce, procurement systems, and supply chain operations. The gap between what manufacturers provide and what commerce platforms need creates friction, lost sales, and operational inefficiency.

**The system must bridge this gap** by automatically generating structured, validated, and explainable product intelligence from these three input fields alone.

---

## 3. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      AI PRODUCT INTELLIGENCE PLATFORM                        │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         FRONTEND (React + MUI)                       │   │
│  │                                                                      │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────┐  │   │
│  │  │  Home    │  │ Analysis │  │ History  │  │  About   │  │Dashboard│  │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                               │ Axios HTTP                                  │
│                               ▼                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                     FASTAPI BACKEND (Python 3.11)                     │   │
│  │                                                                      │   │
│  │  ┌────────────────────────────────────────────────────────────────┐  │   │
│  │  │  API Layer (REST)                                            │  │   │
│  │  │  POST /analyze │ POST /upload-document │ GET /history         │  │   │
│  │  │  GET /health   │ GET /download-json    │ GET /download-pdf    │  │   │
│  │  └────────────────────────────────────────────────────────────────┘  │   │
│  │                               │                                       │   │
│  │                               ▼                                       │   │
│  │  ┌────────────────────────────────────────────────────────────────┐  │   │
│  │  │              MULTI-AGENT ORCHESTRATOR                          │  │   │
│  │  │  ┌────────────────────────────────────────────────────────┐   │  │   │
│  │  │  │  Agent 1: Retrieval Agent                              │   │  │   │
│  │  │  │  • Vector search (ChromaDB) • Cache lookup             │   │  │   │
│  │  │  │  • Document chunk retrieval • Spec extraction           │   │  │   │
│  │  │  └──────────────────────┬─────────────────────────────────┘   │  │   │
│  │  │                         ▼                                      │  │   │
│  │  │  ┌────────────────────────────────────────────────────────┐   │  │   │
│  │  │  │  Agent 2: Product Intelligence Agent                   │   │  │   │
│  │  │  │  • Gemini generation • LangChain chain                 │   │  │   │
│  │  │  │  • Title, Description, Specs, Category, Features       │   │  │   │
│  │  │  │  • Applications, SEO Keywords                          │   │  │   │
│  │  │  └──────────────────────┬─────────────────────────────────┘   │  │   │
│  │  │                         ▼                                      │  │   │
│  │  │  ┌────────────────────────────────────────────────────────┐   │  │   │
│  │  │  │  Agent 3: Validation & Confidence Agent               │   │  │   │
│  │  │  │  • Hallucination detection • Source comparison         │   │  │   │
│  │  │  │  • Confidence scoring • Validation report              │   │  │   │
│  │  │  │  • Source attribution                                  │   │  │   │
│  │  │  └────────────────────────────────────────────────────────┘   │  │   │
│  │  └────────────────────────────────────────────────────────────────┘  │   │
│  │                               │                                       │   │
│  │                               ▼                                       │   │
│  │  ┌────────────────────────────────────────────────────────────────┐  │   │
│  │  │           AI & DATA LAYER                                     │  │   │
│  │  │                                                               │  │   │
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐    │  │   │
│  │  │  │  Google      │  │  ChromaDB    │  │  LangChain       │    │  │   │
│  │  │  │  Gemini API  │  │  Vector DB   │  │  Orchestration   │    │  │   │
│  │  │  │  • gemini-2  │  │  • product   │  │  • Prompt        │    │  │   │
│  │  │  │  • embed-004 │  │    cache     │  │    templates     │    │  │   │
│  │  │  │              │  │  • document   │  │  • Chains        │    │  │   │
│  │  │  │              │  │    chunks    │  │  • Output parsers│    │  │   │
│  │  │  │              │  │  • embeddings│  │  • Retrievers    │    │  │   │
│  │  │  └──────────────┘  └──────────────┘  └──────────────────┘    │  │   │
│  │  └────────────────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                               │                                              │
│                               ▼                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                       DEPLOYMENT                                     │   │
│  │  ┌──────────────────────────┐      ┌──────────────────────────────┐  │   │
│  │  │  Frontend (Vercel)       │      │  Backend (Render)            │  │   │
│  │  │  • React SPA             │      │  • FastAPI + Uvicorn         │  │   │
│  │  │  • Static hosting        │      │  • ChromaDB persistent       │  │   │
│  │  │  • CDN delivery          │      │  • Gemini API integration    │  │   │
│  │  └──────────────────────────┘      └──────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Technology Stack

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| **Frontend** | React | 18.x | Component-based UI framework |
| | Material UI | 5.x | Enterprise-grade component library |
| | Axios | 1.x | HTTP client for API communication |
| | React Router | 6.x | Client-side routing |
| | Recharts | 2.x | Confidence meter visualization |
| **Backend** | Python | 3.11 | Runtime environment |
| | FastAPI | 0.110+ | Async REST API framework |
| | Uvicorn | 0.27+ | ASGI server |
| | Pydantic v2 | 2.x | Request/response validation |
| | ReportLab | 4.x | PDF report generation |
| **AI/ML** | Google Gemini API | Latest | LLM for generation & analysis |
| | LangChain | 0.3+ | LLM orchestration & chain building |
| | ChromaDB | 0.5+ | Vector database for RAG |
| **Deployment** | Vercel | — | Frontend hosting |
| | Render | — | Backend hosting with persistent disk |

---

## 5. Multi-Agent Design

### 5.1 Agent Architecture Overview

The system employs exactly **three specialized agents** working in sequence. Each agent has a single responsibility, well-defined inputs and outputs, and communicates through a shared context object. This modular design enables independent development, testing, and future enhancement.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MULTI-AGENT ORCHESTRATION                            │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        SHARED CONTEXT                                 │   │
│  │  request_id | input | agent_results | errors | timeline | metadata   │   │
│  └──────────┬───────────────────────────────────────────────────────────┘   │
│             │                                                                │
│     ┌───────┴──────────┐     ┌───────────────┴────────────┐                 │
│     ▼                  ▼     ▼                            ▼                  │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  AGENT 1                     AGENT 2                     AGENT 3    │   │
│  │  ┌──────────────────────┐  ┌──────────────────────┐  ┌──────────┐   │   │
│  │  │                     │  │                     │  │          │   │   │
│  │  │   RETRIEVAL        │  │   PRODUCT           │  │VALIDATION│   │   │
│  │  │   AGENT             │──▶│   INTELLIGENCE      │──▶│   &      │   │   │
│  │  │                     │  │   AGENT             │  │CONFIDENCE│   │   │
│  │  │                     │  │                     │  │  AGENT   │   │   │
│  │  └──────────────────────┘  └──────────────────────┘  └──────────┘   │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  INPUT → Agent 1 → Agent 2 → Agent 3 → VALIDATED OUTPUT                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Agent 1: Retrieval Agent

**Role:** Information gatherer and context provider.

**Input:** `ProductRequest { mpn: str, brand: str, description: str }`

**Responsibilities:**
- Query ChromaDB for semantically similar products using vector embeddings
- Perform exact MPN match lookup in the `product_cache` collection
- Retrieve relevant document chunks from the `document_chunks` collection
- Check the `product_cache` for previously enriched results (cache hit)
- Extract product specifications from retrieved documents
- Score and rank all retrieved information by relevance

**Process Flow:**
```
1. Normalize input (uppercase MPN, strip whitespace)
2. Generate embedding vector for query text
3. Parallel queries:
   a. Semantic search → product_cache (top-5)
   b. MPN exact match → product_cache
   c. Semantic search → document_chunks (top-5)
4. Merge results with relevance scoring
5. If cache hit with confidence > 0.95 → return cached result (skip pipeline)
6. Output: RetrievedContext
```

**Output:** `RetrievedContext { documents: List[Document], sources: List[Source], cache_hit: bool, relevance_scores: Dict }`

### 5.3 Agent 2: Product Intelligence Agent

**Role:** Generative AI engine for structured product enrichment.

**Input:** `ProductRequest + RetrievedContext`

**Responsibilities:**
- Generate a professional product **Title** (e.g., "SN74LS00N Quad 2-Input Positive-NAND Gate IC")
- Generate a detailed, SEO-optimized **Description** (2-3 paragraphs)
- Generate a structured **Specifications** table (voltage, current, package, temp range, etc.)
- Identify primary and secondary **Applications** (e.g., "Digital logic circuits, Signal processing")
- Generate **SEO Keywords** for e-commerce discovery
- Identify key product **Features** (bullet points)
- Assign a hierarchical **Category** (e.g., "Semiconductors > Logic ICs > NAND Gates")

**Process Flow:**
```
1. Construct augmented prompt with:
   - System instruction (role, task, output format)
   - Retrieved context (documents with relevance scores)
   - Few-shot examples (3 example enrichments)
   - User query (MPN, Brand, Description)
2. Invoke Gemini via LangChain chain
3. Parse structured JSON output using Pydantic model
4. Validate all required fields are present
5. If JSON parse fails → retry with temperature=0.3
6. Output: EnrichedProduct
```

**Output:** `EnrichedProduct { title, description, specifications, applications, seo_keywords, features, category }`

### 5.4 Agent 3: Validation & Confidence Agent

**Role:** Quality assurance, hallucination detection, and provenance tracking.

**Input:** `EnrichedProduct + RetrievedContext`

**Responsibilities:**
- Validate every generated attribute against the retrieved context documents
- Detect hallucinations (attributes not supported by any source)
- Assign per-attribute confidence scores (0.0 – 1.0)
- Calculate an overall confidence score
- Generate a detailed validation report with pass/fail/partial status per attribute
- Map every attribute to its source document(s) for provenance
- Flag low-confidence items for human review

**Confidence Scoring Formula:**
```
confidence = 0.35 × source_support + 0.25 × validation_status
           + 0.20 × source_count     + 0.10 × consistency
           + 0.10 × attribute_type_boost

Where:
  source_support    = proportion of attribute confirmed by sources
  validation_status = 1.0 (verified), 0.5 (partial), 0.0 (unverified)
  source_count      = min(source_count / 3, 1.0)  (capped at 3 sources)
  consistency       = internal consistency check score
  attribute_type_boost = 0.1 for critical specs (MPN, Brand), 0 for others
```

**Process Flow:**
```
1. For each attribute in EnrichedProduct:
   a. Search retrieved context for supporting evidence
   b. Check for contradictions with source documents
   c. Assign verification status: verified | partial | unverified | contradicted
   d. Calculate attribute confidence score
   e. Map to source documents
2. Calculate overall confidence score (weighted average)
3. Generate validation report
4. Generate source attribution map
5. Output: ValidationResult
```

**Output:** `ValidationResult { confidence_scores, validation_report, source_attributions, overall_confidence }`

---

## 6. RAG Pipeline

### 6.1 Pipeline Overview

The Retrieval-Augmented Generation pipeline is the core intelligence mechanism. It enriches the Gemini LLM's generation with factual context retrieved from ChromaDB, reducing hallucinations and improving accuracy.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RAG PIPELINE                                        │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  STEP 1: DOCUMENT INGESTION                                         │   │
│  │                                                                      │   │
│  │  User uploads PDF/datasheet ──▶ Text extraction ──▶ Chunking         │   │
│  │  (e.g., TI datasheet PDF)       (PyPDF2)          (500 chars,       │   │
│  │                                                    50 overlap)      │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                               ▼                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  STEP 2: EMBEDDING GENERATION                                       │   │
│  │                                                                      │   │
│  │  Each chunk ──▶ Google text-embedding-004 ──▶ 768-dim vector         │   │
│  │  Stored in ChromaDB collection: document_chunks                      │   │
│  │  Metadata stored: source_url, chunk_index, mpn, brand                │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                               ▼                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  STEP 3: QUERY EMBEDDING                                            │   │
│  │                                                                      │   │
│  │  User input (MPN + Brand + Desc) ──▶ text-embedding-004 ──▶         │   │
│  │  768-dim query vector                                                │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                               ▼                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  STEP 4: VECTOR SEARCH                                              │   │
│  │                                                                      │   │
│  │  ChromaDB similarity search with query vector                        │   │
│  │  Collections queried:                                                │   │
│  │  • product_cache (top-3) ──▶ Previously enriched products            │   │
│  │  • document_chunks (top-5) ──▶ Relevant spec chunks                  │   │
│  │                                                                      │   │
│  │  Score threshold: 0.65 (minimum cosine similarity)                   │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                               ▼                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  STEP 5: CONTEXT ASSEMBLY                                           │   │
│  │                                                                      │   │
│  │  Retrieved documents ranked by score ──▶ Top-K context assembled     │   │
│  │  Format: "Source [score]: [document text]"                           │   │
│  │  Truncated to fit token window (Gemini 2.0: 1M tokens)              │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                               ▼                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  STEP 6: AUGMENTED GENERATION                                       │   │
│  │                                                                      │   │
│  │  Construct LangChain prompt:                                         │   │
│  │  System: "You are a product intelligence expert..."                  │   │
│  │  Context: [Retrieved documents]                                      │   │
│  │  Query: "Enrich this product: MPN={mpn}, Brand={brand}..."          │   │
│  │                                                                      │   │
│  │  Gemini generates structured JSON output                             │   │
│  │  LangChain StrOutputParser extracts text                             │   │
│  │  Pydantic parser validates structure                                 │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                               ▼                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  STEP 7: OUTPUT                                                     │   │
│  │                                                                      │   │
│  │  EnrichedProduct with source attributions                            │   │
│  │  Stored in product_cache for future retrieval                        │   │
│  │  Returned to orchestrator for validation                             │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Chunking Strategy

| Parameter | Value | Rationale |
|---|---|---|
| Chunk size | 500 characters | Balances context richness with precision |
| Chunk overlap | 50 characters | Maintains context continuity across boundaries |
| Splitting strategy | RecursiveCharacterTextSplitter | Semantic-aware splitting by paragraphs, then sentences |
| Metadata stored | source_url, mpn, brand, chunk_index | Enables source attribution back to original document |

---

## 7. Database Design

### 7.1 ChromaDB Collections

ChromaDB is a lightweight, embeddable vector database. It stores data as collections of documents, each with an embedding vector and associated metadata.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CHROMADB COLLECTIONS                                │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  COLLECTION 1: product_cache                                        │   │
│  │                                                                      │   │
│  │  Purpose: Cache enriched product intelligence for fast retrieval     │   │
│  │  TTL: 24 hours (stale entries evicted by background job)             │   │
│  │                                                                      │   │
│  │  ┌──────────────┬──────────────────┬─────────────────────────────┐  │   │
│  │  │ Field         │ Type             │ Example                     │  │   │
│  │  ├──────────────┼──────────────────┼─────────────────────────────┤  │   │
│  │  │ id            │ string           │ cache_74LS00_abc123         │  │   │
│  │  │ embedding     │ float[768]       │ [0.023, -0.157, ...]       │  │   │
│  │  │ metadata.mpn  │ string           │ SN74LS00N                   │  │   │
│  │  │ metadata.brand│ string           │ Texas Instruments           │  │   │
│  │  │ metadata.ts   │ string (ISO)     │ 2025-01-15T10:30:00Z       │  │   │
│  │  │ metadata.conf │ float            │ 0.94                        │  │   │
│  │  │ document      │ string (JSON)    │ {"title": "...", ...}       │  │   │
│  │  └──────────────┴──────────────────┴─────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  COLLECTION 2: document_chunks                                      │   │
│  │                                                                      │   │
│  │  Purpose: Store chunked technical documents for RAG retrieval        │   │
│  │  Source: User-uploaded PDFs, datasheets, spec sheets                 │   │
│  │                                                                      │   │
│  │  ┌───────────────┬──────────────────┬────────────────────────────┐  │   │
│  │  │ Field          │ Type             │ Example                    │  │   │
│  │  ├───────────────┼──────────────────┼────────────────────────────┤  │   │
│  │  │ id             │ string           │ chunk_001_002              │  │   │
│  │  │ embedding      │ float[768]       │ [0.101, 0.234, ...]       │  │   │
│  │  │ metadata.mpn   │ string           │ SN74LS00N                  │  │   │
│  │  │ metadata.source│ string           │ ti_datasheet_sn74ls00.pdf  │  │   │
│  │  │ metadata.url   │ string           │ https://ti.com/...        │  │   │
│  │  │ metadata.chunk │ int              │ 2                          │  │   │
│  │  │ document       │ string           │ "The SN74LS00N contains..."│  │   │
│  │  └───────────────┴──────────────────┴────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  COLLECTION 3: embeddings (metadata store)                          │   │
│  │                                                                      │   │
│  │  Purpose: Store embedding model metadata and usage tracking          │   │
│  │  Note: ChromaDB handles embeddings internally; this collection       │   │
│  │  stores configuration metadata, not the vectors themselves.          │   │
│  │                                                                      │   │
│  │  ┌──────────────┬──────────────────┬─────────────────────────────┐  │   │
│  │  │ Field         │ Type             │ Example                     │  │   │
│  │  ├──────────────┼──────────────────┼─────────────────────────────┤  │   │
│  │  │ id            │ string           │ model_config                │  │   │
│  │  │ metadata.model│ string           │ text-embedding-004          │  │   │
│  │  │ metadata.dim  │ int              │ 768                         │  │   │
│  │  │ metadata.total│ int              │ 1250                        │  │   │
│  │  │ document      │ string           │ "Embedding metadata log"    │  │   │
│  │  └──────────────┴──────────────────┴─────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 8. API Design

### 8.1 Endpoint Summary

| Method | Endpoint | Description | Auth | Rate Limit |
|---|---|---|---|---|
| `POST` | `/api/v1/analyze` | Analyze product and generate intelligence | API Key | 10/min |
| `POST` | `/api/v1/upload-document` | Upload product document (PDF) for RAG | API Key | 5/min |
| `GET` | `/api/v1/history` | Get analysis history | API Key | 30/min |
| `GET` | `/api/v1/health` | Health check endpoint | None | 60/min |
| `GET` | `/api/v1/download-json/{id}` | Download analysis as JSON | API Key | 10/min |
| `GET` | `/api/v1/download-pdf/{id}` | Download analysis as PDF report | API Key | 10/min |

### 8.2 Endpoint Details

**POST /api/v1/analyze**

```
Purpose:     Core endpoint — accepts product info and returns enriched intelligence
Request:     { mpn: str, brand: str, description: str }
Response:    { product_id, status, enriched_data, confidence_scores,
               validation, sources, agent_timeline, metadata }
Status:      200 OK | 400 Bad Request | 429 Too Many Requests | 503 Service Unavailable
```

**POST /api/v1/upload-document**

```
Purpose:     Upload technical documents (datasheets, spec sheets) for RAG ingestion
Request:     multipart/form-data { file: PDF, mpn: str (optional) }
Response:    { document_id, chunks_created, status }
Processing:  Extract text → Chunk → Embed → Store in document_chunks
Status:      201 Created | 400 Bad Request | 413 Payload Too Large
```

**GET /api/v1/history**

```
Purpose:     Retrieve paginated history of all product analyses
Query:       ?page=1&limit=10&sort=desc
Response:    { results: List[AnalysisSummary], total, page, limit }
Status:      200 OK
```

**GET /api/v1/health**

```
Purpose:     Health check endpoint for monitoring and deployment verification
Response:    { status: "healthy", version: "2.0.0", uptime: 3600,
               chromadb: "connected", gemini: "available" }
Status:      200 OK | 503 Service Unavailable
```

**GET /api/v1/download-json/{product_id}**

```
Purpose:     Download structured intelligence as JSON file
Response:    Content-Disposition: attachment; filename="product_{id}.json"
             Content-Type: application/json
Status:      200 OK | 404 Not Found
```

**GET /api/v1/download-pdf/{product_id}**

```
Purpose:     Download professional PDF report with all intelligence data
Response:    Content-Disposition: attachment; filename="product_{id}.pdf"
             Content-Type: application/pdf
Status:      200 OK | 404 Not Found | 500 Internal Server Error
```

---

## 9. Frontend Design

### 9.1 Page Structure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      REACT FRONTEND — PAGE MAP                              │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  APP SHELL                                                          │   │
│  │  ┌──────────────────────────────────────────────────────────────┐   │   │
│  │  │  Header (App Bar with logo, navigation, theme toggle)        │   │   │
│  │  ├──────────────────────────────────────────────────────────────┤   │   │
│  │  │                                                              │   │   │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │   │   │
│  │  │  │  HOME    │  │ ANALYSIS │  │ HISTORY  │  │  ABOUT   │   │   │   │
│  │  │  │          │  │          │  │          │  │          │   │   │   │
│  │  │  │ Hero     │  │ Input    │  │ Table of │  │ Project  │   │   │   │
│  │  │  │ section  │  │ form     │  │ past     │  │ info     │   │   │   │
│  │  │  │ Quick    │  │ Dashboard│  │ analyses │  │ Team     │   │   │   │
│  │  │  │ start    │  │ (results)│  │ Search   │  │ Tech     │   │   │   │
│  │  │  │          │  │ Export   │  │ Filter   │  │ stack    │   │   │   │
│  │  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │   │   │
│  │  │                                                              │   │   │
│  │  ├──────────────────────────────────────────────────────────────┤   │   │
│  │  │  Footer (Links, copyright, version)                         │   │   │
│  │  └──────────────────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.2 Page Descriptions

**Home Page**
- Hero section with value proposition: "Turn minimal product data into rich commerce intelligence"
- Three-step quick start guide: (1) Enter MPN, Brand, Description (2) AI Enriches (3) Export
- Feature highlights with icons (confidence scoring, source attribution, RAG pipeline)
- Call-to-action button to navigate to Analysis page
- Responsive design for mobile and desktop

**Analysis Page**
- Two-panel layout: Input form (left) / Dashboard (right)
- **Input Form:** Text fields for MPN, Brand, Description; Submit button with loading state
- **Loading State:** Animated agent timeline showing progress: Retrieval → Intelligence → Validation
- **Dashboard:** (see Section 10 for full details)
- **Export Section:** Download JSON and PDF buttons at bottom of dashboard

**History Page**
- Data table with columns: MPN, Brand, Description, Overall Confidence, Timestamp, Actions
- Search bar for filtering by MPN or Brand
- Sort by date, confidence, or brand
- Click row → navigate to Analysis page with that product's results
- Empty state with illustration when no history exists

**About Page**
- Project description and hackathon context
- Architecture overview (simplified diagram)
- Technology stack cards with icons
- Team information (if applicable)
- Open source links and acknowledgments

---

## 10. Dashboard Components

The dashboard is the most important UI component — it displays all generated intelligence in a clear, organized, visually appealing layout.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ANALYSIS DASHBOARD                                  │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  HEADER                                                             │   │
│  │  Product Title: SN74LS00N Quad 2-Input Positive-NAND Gate IC        │   │
│  │  MPN: SN74LS00N  │  Brand: Texas Instruments  │  Category: ICs      │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────────┐  ┌──────────────────────────────┐ │
│  │  OVERALL CONFIDENCE                  │  │  CONFIDENCE METER            │ │
│  │                                      │  │                              │ │
│  │  Score: 94%                          │  │        ┌───────┐            │ │
│  │  Status: ⚠ High Quality             │  │        │  ██   │            │ │
│  │  Attributes verified: 7/8           │  │        │  ██   │            │ │
│  │  Sources used: 3                    │  │        │  ████ │            │ │
│  │                                      │  │        │  ████ │            │ │
│  └──────────────────────────────────────┘  │        │██████│            │ │
│                                             │        │██████│  94%      │ │
│  ┌──────────────────────────────────────┐  │        └───────┘            │ │
│  │  SPECIFICATIONS TABLE                │  │  0%    50%    100%          │ │
│  │                                      │  └──────────────────────────────┘ │
│  │  ┌──────────────┬──────────┬──────┐ │                                    │
│  │  │ Specification │ Value    │Conf.│ │  ┌──────────────────────────────┐ │
│  │  ├──────────────┼──────────┼──────┤ │  │  FEATURES                   │ │
│  │  │ Supply Voltage│ 4.75-5.25│ 0.98│ │  │  • Quad 2-input NAND gates  │ │
│  │  │ Propagation  │ 15ns     │ 0.85│ │  │  • Low power Schottky        │ │
│  │  │ Package      │ PDIP-14  │ 0.99│ │  │  • TTL compatible inputs     │ │
│  │  │ Temp Range   │ 0-70°C   │ 0.92│ │  │  • Standard 74LS series      │ │
│  │  │ Logic Family │ 74LS     │ 0.95│ │  └──────────────────────────────┘ │
│  │  └──────────────┴──────────┴──────┘ │                                    │
│  └──────────────────────────────────────┘  ┌──────────────────────────────┐ │
│                                             │  APPLICATIONS               │ │
│  ┌──────────────────────────────────────┐  │  • Digital logic circuits    │ │
│  │  DESCRIPTION                        │  │  • Signal processing         │ │
│  │                                      │  │  • Microcontroller interfacing│ │
│  │  The SN74LS00N contains four...     │  │  • Industrial control systems │ │
│  │  (2-3 paragraph detailed desc)      │  └──────────────────────────────┘ │
│  └──────────────────────────────────────┘                                    │
│                                                                             │
│  ┌──────────────────────────────────────┐  ┌──────────────────────────────┐ │
│  │  SEO KEYWORDS                        │  │  VALIDATION REPORT           │ │
│  │                                      │  │                              │ │
│  │  #SN74LS00N #NANDGate #TexasInstr   │  │  ✅ MPN: Verified            │ │
│  │  #LogicIC #74LS #DIP14 #Semiconductor│  │  ✅ Brand: Verified          │ │
│  │                                      │  │  ⚠ Specs: Partial (5/7)     │ │
│  └──────────────────────────────────────┘  │  ❌ Alt Parts: Unverified    │ │
│                                             └──────────────────────────────┘ │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  SOURCES                                                            │   │
│  │                                                                      │   │
│  │  📄 TI SN74LS00N Datasheet (relevance: 98%) — ti.com                │   │
│  │  📄 Mouser Electronics Catalog (relevance: 85%) — mouser.com        │   │
│  │  📄 Gemini Knowledge Base (relevance: 72%)                           │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  EXPORT                                                             │   │
│  │                                                                      │   │
│  │  [ 📥 Download JSON ]  [ 📥 Download PDF ]  [ 📋 Copy to Clipboard ]│   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 11. Workflow

### 11.1 Complete Analysis Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      END-TO-END ANALYSIS WORKFLOW                           │
│                                                                             │
│  USER                         SYSTEM                                        │
│  ────────────────────────────────────────────────────────────────────────   │
│                                                                             │
│  [1] Enter MPN, Brand,                                                     │
│      Description                                                           │
│      ─────────────────────────────────────────▶                            │
│                                              │                              │
│                                              ▼                              │
│                                        [2] POST /api/v1/analyze            │
│                                              │                              │
│                                              ▼                              │
│                                        [3] FastAPI validates input         │
│                                        (Pydantic schema check)             │
│                                              │                              │
│                                              ▼                              │
│                                        [4] Orchestrator creates            │
│                                        AgentContext                        │
│                                              │                              │
│              ┌────────────────────────────────┼────────────────────────┐   │
│              ▼                                ▼                        ▼   │
│        [5] Retrieval                  [6] Product                 [7] Val.│
│            Agent                     Intelligence                  & Conf.│
│        • ChromaDB search              Agent                        Agent  │
│        • Cache check                  • Gemini gen.                • Valid.│
│        • Doc retrieval                • LangChain                  • Score │
│        • Spec extraction              • Structured                 • Sourc.│
│              │                         output                       │      │
│              └────────────────────────┬────────────────────────────┘      │
│                                       ▼                                    │
│                                 [8] Orchestrator aggregates                │
│                                 results                                   │
│                                       │                                    │
│                                       ▼                                    │
│                                 [9] Store in product_cache                │
│                                 (ChromaDB)                                 │
│                                       │                                    │
│                                       ▼                                    │
│                                 [10] Return JSON response                  │
│                                       │                                    │
│              ◀─────────────────────────────────────────────────────────    │
│                                                                             │
│  [11] Dashboard renders                                                    │
│  • Confidence meter     • Specs table    • Features                        │
│  • Applications         • SEO Keywords   • Validation report               │
│  • Sources              • Export buttons                                   │
│                                                                             │
│  [12] User exports JSON or PDF                                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 11.2 Agent Timeline (Frontend Visualization)

During analysis, the frontend displays a real-time timeline showing agent progress:

```
⏳ Analyzing SN74LS00N...

[████████░░░░░░░░░░░░] 45%

  Agent Timeline:
  ┌────────────────────────────────────────────────────────────────┐
  │ ✅ Retrieval Agent         320ms  — 3 documents retrieved    │
  │ ⏳ Product Intelligence    1.2s   — Generating...           │
  │ ⏳ Validation & Confidence  —      — Pending...             │
  └────────────────────────────────────────────────────────────────┘
```

---

## 12. Security Architecture

### 12.1 Security Layers

| Layer | Measure | Implementation |
|---|---|---|
| **Environment** | API Key Management | `.env` file with `GEMINI_API_KEY`, `CHROMA_DB_PATH` |
| **Backend** | API Key Protection | FastAPI dependency injection, Bearer token validation |
| **Backend** | Input Validation | Pydantic v2 models with strict type checking |
| **Backend** | Rate Limiting | SlowAPI middleware — 10 req/min for /analyze |
| **Backend** | CORS | Restricted to Vercel frontend domain |
| **Backend** | Request Size Limit | 10MB max for document uploads |
| **Frontend** | Environment Variables | `REACT_APP_API_URL` — no secrets exposed |
| **Network** | HTTPS | Enforced at Vercel and Render edge |

### 12.2 Rate Limiting Configuration

```
POST /api/v1/analyze           → 10 requests per minute per IP
POST /api/v1/upload-document   → 5 requests per minute per IP
GET  /api/v1/history           → 30 requests per minute per IP
GET  /api/v1/health            → 60 requests per minute per IP
GET  /api/v1/download-json     → 10 requests per minute per IP
GET  /api/v1/download-pdf      → 10 requests per minute per IP
```

---

## 13. Performance Considerations

### 13.1 Performance Strategies

| Strategy | Implementation | Expected Impact |
|---|---|---|
| **Caching** | ChromaDB product_cache with 24h TTL | 80% reduction in Gemini API calls for repeat queries |
| **Async FastAPI** | All endpoints use `async def` with `await` | 5x concurrent request handling |
| **Connection Pooling** | Reuse ChromaDB and HTTP connections | 40% reduction in connection overhead |
| **Lazy Loading** | Dashboard components load on-demand | 60% faster initial page load |
| **Chunking** | Documents chunked before embedding | Handles documents up to 100 pages |
| **Token Management** | Truncate context to fit Gemini context window | Prevents token overflow errors |

### 13.2 Expected Performance Metrics

| Metric | Target |
|---|---|
| **Analysis Time** (cold start) | < 5 seconds |
| **Analysis Time** (cache hit) | < 500ms |
| **Document Upload + Ingestion** | < 3 seconds per 10 pages |
| **API Response Time** (p95) | < 2 seconds |
| **Frontend Load Time** | < 2 seconds initial load |
| **Concurrent Users** | 50 (Render free tier) |

---

## 14. Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DEPLOYMENT ARCHITECTURE                             │
│                                                                             │
│  ┌──────────────────────────────────────┐   ┌────────────────────────────┐  │
│  │         VERCEL (Frontend)            │   │       RENDER (Backend)     │  │
│  │                                      │   │                            │  │
│  │  ┌────────────────────────────────┐  │   │  ┌──────────────────────┐  │  │
│  │  │  React SPA                     │  │   │  │  FastAPI + Uvicorn   │  │  │
│  │  │  • Static build (npm run build)│  │   │  │  • Python 3.11       │  │  │
│  │  │  • CDN cached                 │  │   │  │  • Async workers     │  │  │
│  │  │  • Automatic HTTPS            │  │   │  │  • Health checks     │  │  │
│  │  │  • Environment variables      │  │   │  │  • Logging           │  │  │
│  │  └────────────────────────────────┘  │   │  └──────────────────────┘  │  │
│  │                                      │   │                            │  │
│  │  URL: https://product-intel.vercel│  │   │  ├──────────────────────┐  │  │
│  │                                      │   │  │  ChromaDB (persistent)│  │  │
│  └──────────────────────────────────────┘   │  │  • Disk storage      │  │  │
│                                              │  │  • /data/chromadb   │  │  │
│                                              │  │  • Backups          │  │  │
│                                              │  └──────────────────────┘  │  │
│                                              │                            │  │
│                                              │  URL: https://api.render │  │
│                                              └────────────────────────────┘  │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  ENVIRONMENT VARIABLES                                              │   │
│  │                                                                      │   │
│  │  Vercel:                   Render:                                   │   │
│  │  REACT_APP_API_URL         GEMINI_API_KEY                            │   │
│  │                            CHROMA_DB_PATH=/data/chromadb             │   │
│  │                            CORS_ORIGINS=https://product-intel.vercel │   │
│  │                            RATE_LIMIT_ENABLED=true                   │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 15. Future Features

| Feature | Priority | Description | Complexity |
|---|---|---|---|
| **Batch CSV Processing** | High | Upload CSV of products for bulk enrichment | Medium |
| **Product Comparison** | Medium | Side-by-side comparison of multiple products | Medium |
| **Feedback Learning** | Medium | User feedback updates confidence scores dynamically | High |
| **Image OCR** | Low | Extract MPN from product images using OCR | High |
| **Human Review** | Low | Manual review queue for low-confidence results | Medium |
| **Real-time Web Search** | Medium | Google Search API for datasheet discovery | Medium |
| **Multi-language** | Low | Generate product descriptions in multiple languages | Medium |
| **Price Intelligence** | Medium | Real-time pricing from distributor APIs | High |

---

## 16. Conclusion

### Why This Architecture is Scalable

The three-agent architecture is horizontally scalable because each agent is stateless and communicates through a shared context object. The retrieval agent can be backed by a distributed ChromaDB cluster, the intelligence agent can be parallelized across multiple Gemini API calls, and the validation agent can run independently. FastAPI's async nature means the backend can handle hundreds of concurrent requests on a single instance.

### Why This Architecture is Explainable

Every attribute generated by the system includes a confidence score and a source attribution. The validation agent explicitly checks each attribute against retrieved context, flagging contradictions and unverifiable claims. The agent timeline provides a complete audit trail of the analysis process. This explainability is critical for industrial commerce, where procurement decisions rely on trustable, auditable data.

### Why This Architecture is Suitable for Industrial Commerce

Industrial commerce demands precision, reliability, and trust. This architecture delivers:
- **Accuracy** through RAG — Gemini generates outputs grounded in retrieved documents, not from memory alone
- **Trust** through confidence scoring and source attribution — every claim is traceable
- **Efficiency** through caching — repeat queries return instantly
- **Practicality** through a focused three-agent design — achievable in a hackathon while demonstrating advanced AI engineering
- **Scalability** through cloud-native deployment — Vercel for frontend, Render for backend, with persistent ChromaDB storage

The AI Product Intelligence Platform transforms the industrial commerce workflow from manual, error-prone data entry to an automated, intelligent, explainable pipeline — turning minimal manufacturer data into a competitive advantage.

---

*End of Architecture Document*

**AI Product Intelligence Platform** | UniHack by Unilog | August 2026
