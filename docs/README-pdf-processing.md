# PDF Processing and Retrieval Sequence (Session In-Memory)

This document defines the recommended end-to-end sequence to handle user requests when an uploaded PDF is available in session memory, while protecting existing behavior and avoiding regressions.

## Goals

1. Preserve current retrieval quality and behavior for existing DB-backed RAG.
2. Add uploaded-PDF support as an optional enhancement, not a replacement.
3. Keep latency controlled and predictable.
4. Avoid brittle routing decisions that could skip important retrieval paths.
5. Keep architecture maintainable with minimal disruption to the current agent.

## Non-Goals

1. Replacing the existing semantic/BM25 pipeline.
2. Building persistent per-user document memory across restarts.
3. Hard-routing all requests exclusively to uploaded PDF or DB sources.

## Current Baseline (Before Session-PDF Retrieval Integration)

1. User question enters the graph.
2. Query rewrite.
3. Semantic search (+ BM25/hybrid path when enabled).
4. Global reranker.
5. Final answer generation.

Session PDF scanning and in-memory indexing exist in UI, but those chunks are not yet fused into retrieval in the baseline.

## Recommended Sequence (Target Behavior)

### 1) Pre-Check

1. If no session PDF is loaded, execute the current pipeline unchanged.
2. If session PDF exists, continue with the augmented flow below.

### 2) Query Intent Classification (Lightweight, Rule-Based)

1. Classify request as:
   - `summary_like`
   - `qa_like`
2. Use deterministic rules/keywords (no extra LLM call in first version).
3. Classification should tune retrieval budgets only, not disable core DB retrieval.

Examples of `summary_like` indicators:
- summarize
- summary
- overview
- key points
- key takeaways
- this document / entire document / uploaded doc
- riassumi / sintesi / panoramica / resume

### 3) Multi-Source Retrieval (Always Keep Baseline Path)

1. Always run existing DB retrieval:
   - semantic path
   - BM25/hybrid path (as currently configured)
2. If session PDF exists, also query the session in-memory vector store.
3. Session retrieval `k` is intent-dependent:
   - `qa_like`: low `k` (example: 3)
   - `summary_like`: higher `k` (example: 15 to 30)

Important: DB retrieval budget must not be reduced by introducing session retrieval.

### 4) Merge and Deduplicate

1. Merge candidates from:
   - semantic retrieval
   - BM25/hybrid retrieval
   - session-PDF retrieval
2. Deduplicate by normalized content (same approach as existing hybrid dedupe logic).
3. Preserve source metadata so references remain explainable:
   - `retrieval_type = semantic`
   - `retrieval_type = bm25`
   - `retrieval_type = session_pdf_vlm`

### 5) Candidate Capping (Latency Guardrail)

1. Apply a hard cap to total candidates before reranker.
2. Cap should be configurable (example: 20 or 25).
3. Cap strategy should keep DB non-regression:
   - first keep DB baseline candidates
   - then add session candidates up to cap
   - do not shrink existing DB baseline below current settings

### 6) Single Reranker Pass

1. Use one global reranker call over merged candidates.
2. Avoid double reranking in initial design to control latency/cost.
3. Let reranker perform final relevance selection across all sources.

### 7) Final Answer Generation

1. Use reranker-selected chunks to build context.
2. Generate final answer as in current flow.
3. References should include source and retrieval type, without exposing raw chunk text in UI.

## Why This Sequence

1. Avoids hard routing errors:
   - misclassification does not skip DB retrieval.
2. Minimizes regression risk:
   - existing DB path remains intact.
3. Controls performance:
   - intent-based session `k` + total cap + one reranker pass.
4. Keeps implementation incremental:
   - no full redesign required.

## Risk Analysis

### Accuracy Risks

1. Intent misclassification:
   - Mitigation: classification adjusts budgets only; does not disable DB path.
2. Reranker dropping useful context for broad summaries:
   - Mitigation: higher `summary_like` session budget and configurable caps.
3. VLM OCR imperfections:
   - Mitigation: page limits, prompt refinement, observability on OCR yield.

### Performance Risks

1. Larger candidate set increases reranker latency.
   - Mitigation: intent-based budgets and total cap.
2. Session retrieval overhead.
   - Mitigation: small `qa_like` `k`; only query session store when it exists.

### Operational Risks

1. Session memory growth with large PDFs.
   - Mitigation: `SESSION_PDF_MAX_PAGES`, optional file size cap, single active session doc in POC.
2. Non-portability across replicas/restarts.
   - Accepted for current session-scoped design.

## Non-Regression Policy

To ensure current behavior is not degraded:

1. DB retrieval settings remain unchanged.
2. Session retrieval is additive, never substitutive.
3. Feature flag available for quick disablement.
4. Instrumentation required before/after enablement.

## Suggested Config Controls

1. `ENABLE_SESSION_PDF_RETRIEVAL` (bool)
2. `SESSION_PDF_TOP_K_QA` (int, low budget)
3. `SESSION_PDF_TOP_K_SUMMARY` (int, high budget)
4. `SESSION_PDF_MAX_PAGES` (already present)
5. `MAX_CANDIDATES_BEFORE_RERANK` (global cap)
6. Optional: `ENABLE_SESSION_PDF_INTENT_CLASSIFIER` (bool)

## Observability Requirements

Log per request:

1. Session PDF presence (yes/no)
2. Intent class (`qa_like` or `summary_like`)
3. Candidate counts by source:
   - semantic
   - bm25/hybrid
   - session
4. Merged count and post-dedupe count
5. Pre-reranker capped count
6. Step timings:
   - session retrieval
   - reranker
   - final generation
7. Retry attempts/errors (already partially implemented for LLM calls)

## Rollout Strategy

### Phase 1 (Safe Intro)

1. Keep feature disabled by default.
2. Enable in controlled test environment.
3. Use conservative settings:
   - `qa_like` low
   - `summary_like` moderate
4. Validate:
   - no regression on normal Q/A
   - improved behavior on uploaded-doc queries

### Phase 2 (Tune)

1. Analyze logs and latency distributions.
2. Tune session budgets and cap.
3. Expand summary budget only if needed.

### Phase 3 (Production Hardening)

1. Add tests for intent rules and merge/dedupe behavior.
2. Add regression suite with and without session PDF.
3. Evaluate multi-instance strategy if session continuity is needed.

## Test Scenarios

1. No uploaded PDF:
   - behavior identical to baseline.
2. Uploaded PDF + targeted Q/A:
   - answer uses session doc when relevant.
3. Uploaded PDF + generic unrelated question:
   - DB path still returns correct context.
4. Uploaded PDF + summary request:
   - enough session chunks included to support broad summary.
5. Large uploaded PDF near page limit:
   - accepted up to limit, rejected beyond limit.
6. Error paths:
   - session retrieval failures do not break baseline DB response path.

## Decision Summary

Use a hybrid additive retrieval strategy:

1. Always keep existing DB retrieval.
2. Add session retrieval only when PDF exists.
3. Tune session contribution by intent.
4. Merge + dedupe + cap.
5. Single reranker pass.
6. Maintain strict non-regression guarantees.

