# AXION — Benchmark Dataset Schema Specification

**Document Version:** 1.0.0  
**Phase Target:** Phase 0 Data Architecture  
**Scope:** Pydantic & JSON Schemas for Documents, Questions, and Evaluation Logs  
**Date:** November 19, 2026  

---

## 1. Overview & Schema Design Principles

The AXION Benchmark requires machine-enforceable, strongly typed schemas to guarantee that all synthetic documents, benchmark queries, ground truth annotations, and evaluation execution logs remain consistent across development and locked evaluation runs.

All schemas are specified using standard JSON Schema / Pydantic v2 compatible conventions.

---

## 2. Synthetic Document Schema (`SyntheticDocument`)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "SyntheticDocument",
  "type": "object",
  "required": [
    "document_id",
    "title",
    "domain",
    "text_content",
    "epistemic_tier",
    "is_distractor"
  ],
  "properties": {
    "document_id": {
      "type": "string",
      "pattern": "^doc-[a-z0-9\\-]+$",
      "description": "Unique identifier for the synthetic document."
    },
    "title": {
      "type": "string",
      "description": "Formal academic title of the synthetic publication."
    },
    "authors": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Fictional author names."
    },
    "domain": {
      "type": "string",
      "description": "Disciplinary category, e.g. physics:electromagnetism, materials:thermoelectrics."
    },
    "text_content": {
      "type": "string",
      "description": "Full document prose formatted in clear markdown sections."
    },
    "declared_constants": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "required": ["symbol", "value", "unit", "description"],
        "properties": {
          "symbol": { "type": "string" },
          "value": { "type": "number" },
          "unit": { "type": "string" },
          "description": { "type": "string" }
        }
      }
    },
    "declared_equations": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["equation_id", "latex", "plain_text", "variables"],
        "properties": {
          "equation_id": { "type": "string" },
          "latex": { "type": "string" },
          "plain_text": { "type": "string" },
          "variables": {
            "type": "array",
            "items": { "type": "string" }
          }
        }
      }
    },
    "declared_assumptions": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Explicit physical boundaries, e.g. 'laminar_flow', 'steady_state', 'T > 300K'."
    },
    "applicability_envelope": {
      "type": "object",
      "description": "Permitted numerical ranges for independent variables.",
      "additionalProperties": {
        "type": "object",
        "required": ["min", "max", "unit"],
        "properties": {
          "min": { "type": "number" },
          "max": { "type": "number" },
          "unit": { "type": "string" }
        }
      }
    },
    "planted_conflict": {
      "type": "object",
      "description": "Metadata if this document deliberately contradicts another document.",
      "properties": {
        "conflicts_with_doc_id": { "type": "string" },
        "conflicting_parameter": { "type": "string" },
        "planted_divergence": { "type": "string" }
      }
    },
    "prompt_injection": {
      "type": "object",
      "description": "Adversarial text planted to test security and instruction isolation.",
      "properties": {
        "has_injection": { "type": "boolean" },
        "injection_type": { "type": "string", "enum": ["system_override", "exfiltration", "false_verdict"] },
        "injection_payload": { "type": "string" }
      }
    },
    "epistemic_tier": {
      "type": "string",
      "enum": ["FACT_DOCUMENTED", "HYPOTHESIS_FORMAL", "CONJECTURE"]
    },
    "is_distractor": {
      "type": "boolean",
      "description": "True if document shares keywords but provides no necessary evidence."
    }
  }
}
```

---

## 3. Benchmark Problem Schema (`BenchmarkProblem`)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "BenchmarkProblem",
  "type": "object",
  "required": [
    "problem_id",
    "category",
    "query",
    "ground_truth_answer",
    "expected_verdict"
  ],
  "properties": {
    "problem_id": {
      "type": "string",
      "pattern": "^(CAT[1-6])-[0-9]{3}$",
      "description": "Standardized ID, e.g. CAT1-001 through CAT6-030."
    },
    "category": {
      "type": "string",
      "enum": [
        "RETRIEVAL_AND_EVIDENCE_ID",
        "CLAIM_EXTRACTION",
        "CROSS_DOCUMENT_COMPOSITION",
        "CONFLICTING_SOURCES",
        "UNANSWERABLE_INSUFFICIENT",
        "CROSS_DOMAIN_TRANSFER"
      ]
    },
    "query": {
      "type": "string",
      "description": "Natural language research or engineering question presented to the system."
    },
    "required_document_ids": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Exact list of documents containing the necessary premises."
    },
    "distractor_document_ids": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Irrelevant documents present in the active retrieval index."
    },
    "ground_truth_answer": {
      "type": "string",
      "description": "Gold-standard target answer string or numerical derivation."
    },
    "expected_verdict": {
      "type": "string",
      "enum": ["ANSWERABLE", "ABSTAIN_INSUFFICIENT_EVIDENCE", "CONFLICT_DETECTED", "TRANSFER_ACCEPTED", "TRANSFER_REJECTED"]
    },
    "expected_claims": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["claim_text", "source_doc_id", "verbatim_quote"],
        "properties": {
          "claim_text": { "type": "string" },
          "source_doc_id": { "type": "string" },
          "verbatim_quote": { "type": "string" },
          "governing_conditions": { "type": "array", "items": { "type": "string" } }
        }
      }
    },
    "expected_reasoning_steps": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["step_index", "operation", "premises", "derived_conclusion"],
        "properties": {
          "step_index": { "type": "integer" },
          "operation": { "type": "string" },
          "premises": { "type": "array", "items": { "type": "string" } },
          "derived_conclusion": { "type": "string" }
        }
      }
    },
    "expected_abstention_reason": {
      "type": "string",
      "description": "Mandatory explanation if expected_verdict is ABSTAIN or CONFLICT."
    },
    "memory_seed_id": {
      "type": "string",
      "description": "If Category 6, the ID of the seed verified finding tested."
    }
  }
}
```

---

## 4. Evaluation Execution Result Schema (`EvaluationExecutionRecord`)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "EvaluationExecutionRecord",
  "type": "object",
  "required": [
    "run_id",
    "problem_id",
    "system_condition",
    "timestamp",
    "is_correct",
    "raw_output",
    "metrics"
  ],
  "properties": {
    "run_id": { "type": "string" },
    "problem_id": { "type": "string" },
    "system_condition": {
      "type": "string",
      "enum": ["AXION_PIPELINE", "PLAIN_RAG_BASELINE", "AXION_NO_MEMORY"]
    },
    "timestamp": { "type": "string", "format": "date-time" },
    "raw_output": { "type": "string" },
    "emitted_verdict": { "type": "string" },
    "is_correct": { "type": "boolean" },
    "correct_abstention": { "type": "boolean" },
    "false_transfer": { "type": "boolean" },
    "retrieved_document_ids": {
      "type": "array",
      "items": { "type": "string" }
    },
    "metrics": {
      "type": "object",
      "required": ["retrieval_precision", "retrieval_recall", "citation_accuracy", "latency_ms"],
      "properties": {
        "retrieval_precision": { "type": "number", "minimum": 0, "maximum": 1 },
        "retrieval_recall": { "type": "number", "minimum": 0, "maximum": 1 },
        "evidence_coverage": { "type": "boolean" },
        "claim_precision": { "type": "number" },
        "claim_recall": { "type": "number" },
        "calculation_accuracy": { "type": "boolean" },
        "citation_accuracy": { "type": "number", "minimum": 0, "maximum": 1 },
        "latency_ms": { "type": "number" },
        "token_usage": {
          "type": "object",
          "properties": {
            "prompt_tokens": { "type": "integer" },
            "completion_tokens": { "type": "integer" },
            "total_tokens": { "type": "integer" }
          }
        }
      }
    },
    "reproducibility_metadata": {
      "type": "object",
      "required": ["model_id", "temperature", "prompt_hash"],
      "properties": {
        "model_id": { "type": "string" },
        "temperature": { "type": "number" },
        "seed": { "type": "integer" },
        "prompt_hash": { "type": "string" }
      }
    }
  }
}
```
