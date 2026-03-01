# Regression Eval Set (JSONL)

This document explains how to run a small regression evaluation against the LangGraph workflow.

## Files

- Dataset example: `eval_data/regression_sample.jsonl`
- Runner script: `scripts/eval/run_regression_eval.py`

## Dataset format (JSONL)

One JSON object per line. Required fields:

- `id`: unique test id
- `question`: user question

Optional fields:

- `session_pdf_path`: absolute path to a PDF to load in-memory for this test case
- `expected_intent`: `GLOBAL_KB | SESSION_DOC | HYBRID`
- `expected_sources`: list with `kb` and/or `session_pdf`
- `expected_citations`: list of objects like `{"source":"Doc.pdf","page":"12"}`
- `must_contain`: list of words/phrases expected in final answer

## Example rows

See the sample file:

- `eval_data/regression_sample.jsonl`

Replace `"/ABSOLUTE/PATH/TO/YOUR/UPLOADED_DOC.pdf"` with real paths for `SESSION_DOC` / `HYBRID` cases.

## How to run

From project root:

```bash
PYTHONPATH=$(pwd) python scripts/eval/run_regression_eval.py \
  --dataset eval_data/regression_sample.jsonl
```

Optional flags:

```bash
PYTHONPATH=$(pwd) python scripts/eval/run_regression_eval.py \
  --dataset eval_data/regression_sample.jsonl \
  --out eval_data/regression_results.json \
  --model-id openai.gpt-5.2 \
  --collection-name COLL01 \
  --max-cases 10
```

Disable reranker (A/B check):

```bash
PYTHONPATH=$(pwd) python scripts/eval/run_regression_eval.py \
  --dataset eval_data/regression_sample.jsonl \
  --disable-reranker
```

## Output

The runner writes a JSON report (default: `eval_data/regression_results.json`) with:

- global summary:
  - `pass_rate`
  - `intent_ok_rate`
  - `sources_ok_rate`
  - `citations_ok_rate`
  - `must_contain_ok_rate`
  - `errors_count`
- per-case results (including `predicted_intent`, `observed_sources`, `node_error`, `pass`)

## Notes

- `SESSION_DOC` and `HYBRID` rows need valid `session_pdf_path`.
- The runner executes the real workflow and uses current `config.py` defaults unless overridden by CLI flags.
