# Phase 5 — Structured Data + RAG Hybrid

## Overview

Phase 5 extends the AI Ecommerce Analyst from structured-data tool orchestration into a hybrid architecture that combines deterministic analytical facts with retrieved business knowledge.

The design keeps the existing analytical contract unchanged:

```text
User
→ LLM / Agent
→ Tool
→ Query Service
→ SQL / View
→ SQLite
```

Structured business facts remain deterministic. RAG is used for definitions, interpretation frameworks, customer strategies, product-analysis guidance, trend interpretation, and business recommendations.

The LLM does not query SQLite directly.

## Objectives

Phase 5 was designed around three routing modes:

```text
Structured-only
→ structured analytical tools
→ deterministic business facts

RAG-only
→ business_knowledge_search
→ retrieved business knowledge

Hybrid
→ structured analytical tools
+ business_knowledge_search
→ combined facts + business knowledge
```

The core separation is:

```text
SQL / Query Service
→ What are the facts?

RAG
→ How should the facts be interpreted or acted on?

LLM / Agent
→ Which source should be used and how should evidence be composed?
```

## Knowledge Base

The local knowledge base contains five bilingual Markdown documents:

```text
knowledge/customer_segment_playbook.md
knowledge/sales_trend_interpretation.md
knowledge/product_performance_playbook.md
knowledge/ecommerce_kpi_definitions.md
knowledge/business_recommendation_rules.md
```

Each document contains metadata describing:

```text
domain
use_for
do_not_use_for
structured_source_for_facts
```

The knowledge base intentionally does not replace SQL or introduce new numeric business facts.

## Knowledge Loading and Chunking

`src/rag/knowledge_loader.py` implements lightweight Markdown-based loading and heading-aware chunking.

Current behavior:

- Pure Python implementation
- Heading-based chunk boundaries
- Metadata excluded from retrieval chunks
- English and Chinese content retained
- Document title and language headings excluded from chunk content

The current knowledge base produces 84 chunks.

## Embeddings and Local Vector Store

`src/rag/embedding_provider.py` integrates SiliconFlow embeddings.

Current model:

```text
Qwen/Qwen3-Embedding-0.6B
```

The vector store is implemented locally in `src/rag/vector_store.py` using:

```text
NumPy cosine similarity
JSON persistence
data/rag_index.json
```

The current embedding dimension is 1024.

No external vector database or RAG framework is required.

## Retriever

`src/rag/retriever.py` implements the `KnowledgeRetriever`.

Current retrieval behavior includes:

- Language preference
- Bilingual duplicate suppression
- Low-value section filtering
- Candidate expansion before final top-k selection
- Cross-language fallback rather than hard filtering

`top_k` controls retrieval breadth, not the number of recommendations that must appear in the final answer.

## RAG Tool Integration

The Agent accesses business knowledge through:

```text
business_knowledge_search
```

The Tool is registered through the existing Tool Registry and executed through the Tool Router.

It is intended for:

- Business definitions
- KPI interpretation
- Customer-segment strategies
- Product-performance interpretation
- Trend interpretation
- Business recommendation frameworks

It is not the source of deterministic transactional facts.

## Provenance-Constrained Knowledge Output

A key Phase 5 reliability improvement is deterministic handling of supported customer-segmentation knowledge.

The pipeline is:

```text
Retriever
→ Knowledge Claims
→ Knowledge Selector
→ Knowledge Renderer
```

Relevant modules:

```text
src/rag/knowledge_claims.py
src/rag/knowledge_selector.py
src/rag/knowledge_renderer.py
```

For customer-segmentation knowledge, retrieved content is converted into structured claims such as:

```text
characteristics
recommended_actions
```

When the user's query explicitly names a segment such as Champions, the selector keeps only the matching segment claim.

The renderer then produces the final knowledge text without letting the LLM invent additional examples or operational details.

## Deterministic RAG Mode

For eligible pure RAG questions, the Agent returns:

```text
answer_mode = deterministic_rag
```

Example:

```text
Champions客户应该怎么运营？
```

The final answer is generated directly from selected and rendered knowledge claims.

This avoids free-form LLM expansion such as adding unsupported VIP channels, rebate programs, or other recommendations that were not present in the retrieved knowledge.

## Deterministic Hybrid Mode

For supported hybrid customer-segment questions, the Agent returns:

```text
answer_mode = deterministic_hybrid
```

Example:

```text
Champions客户贡献了多少收入，并且应该怎么运营？
```

The response is composed from:

```text
customer_segments
→ deterministic structured facts

business_knowledge_search
→ deterministic rendered knowledge

Agent
→ deterministic composition
```

This prevents the LLM from changing structured facts or expanding retrieved recommendations during final synthesis.

## General Model Knowledge

The system also supports explicitly requested general ecommerce suggestions.

Example:

```text
除了知识库里的策略，还有哪些通用运营建议？
```

When the user explicitly requests suggestions beyond the knowledge base, the Agent may use model general knowledge.

The final response is deterministically labeled:

```text
通用建议（非知识库内容）

以下建议来自模型通用电商知识，
不属于当前知识库检索内容。
```

This prevents model-generated general advice from being presented as retrieved knowledge.

## Grounding Validator

Phase 5 extends the lightweight deterministic Grounding Validator.

Current checks include:

- Tool execution success
- Unsupported numeric claims
- Unsupported currency or monetary units
- Structured numeric evidence
- Whether a RAG Tool was used
- Whether RAG evidence was available
- Retrieved source tracking

RAG numeric metadata such as similarity scores is excluded from structured numeric evidence.

The validator intentionally remains lightweight and is not a second semantic reasoning model.

## Deterministic Sanitizer

For free-form model answers, unsupported numeric or currency claims may be removed through a deterministic sanitizer.

The sanitizer is intentionally narrow:

```text
unsupported_numbers
unsupported_currency
```

It does not perform semantic rewriting and does not introduce replacement facts.

## Source Alignment

When deterministic knowledge selection produces explicit final sources, Grounding uses those selected sources for provenance display.

If no selected source list exists, it falls back to raw retrieval results for backward compatibility.

This keeps:

```text
final answer
↔ used knowledge
↔ displayed source
```

aligned.

## Streamlit Integration

The AI Analyst Trace now exposes:

```text
Answer Mode
Tool Calls
Tool Results
Grounding Validation
Knowledge Sources
```

`Knowledge Sources` is shown only when retrieved sources are available.

Example modes include:

```text
deterministic_rag
deterministic_hybrid
LLM synthesis with grounded tool evidence
```

## Regression Testing

Phase 5 adds:

```text
tests/test_phase5_regression.py
```

Validated scenarios:

```text
Structured-only
RAG-only
Hybrid
General Suggestions
Phase 4 product-comparison regression
```

Verified result:

```text
ALL PHASE 5 AGENT REGRESSION TESTS PASSED
```

The Streamlit UI was also validated for the main Phase 5 routing scenarios.

## Environment Variables

Phase 5 requires:

```text
SILICONFLOW_API_KEY=your_api_key
SILICONFLOW_MODEL=Qwen/Qwen3-8B
SILICONFLOW_EMBEDDING_MODEL=Qwen/Qwen3-Embedding-0.6B
```

Do not commit `.env` to Git.

## Known Limitations

Phase 5 intentionally remains minimal and demonstrable rather than becoming a large RAG platform.

Known limitations include:

- Deterministic claim extraction is currently strongest for customer-segmentation knowledge
- Other knowledge domains can still rely on retrieved chunks plus LLM synthesis
- Grounding Validation does not perform full semantic entailment or contradiction detection
- Supported numbers can still be described with incorrect semantics by free-form LLM generation
- The knowledge base is local and manually maintained
- There is no reranker, BM25 layer, query rewriting, external vector database, or second LLM judge
- `temperature=0` reduces variance but does not make LLM behavior mathematically deterministic
- General model knowledge is allowed only when explicitly requested and is labeled separately from retrieved knowledge

These limitations are deliberate scope decisions for a portfolio-scale system.

## Phase 5 Result

Phase 5 is complete.

The project now demonstrates:

```text
deterministic structured analytics
+
local semantic retrieval
+
source-aware RAG
+
deterministic knowledge rendering
+
hybrid structured/RAG composition
+
general-knowledge provenance separation
+
lightweight grounding validation
+
observable Streamlit trace
```
