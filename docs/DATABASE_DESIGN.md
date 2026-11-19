# AXION — Database Design & Unified Data Architecture

**Document Version:** 2.0.0  
**Date:** November 18, 2026  
**Status:** Approved for Phase 0 Specification  
**Project:** AXION — Universal Knowledge and Cross-Domain Intelligence Platform  

---

## 1. Storage Architecture Overview

AXION's persistence layer is engineered as a unified, multi-model relational and vector database implemented in **PostgreSQL 16** with the **`pgvector`** extension. It supports all ten platform components without requiring disparate database daemons, guaranteeing atomic ACID transactions across documents, vector embeddings, property graph nodes, reasoning DAGs, and validated memory ledgers.

---

## 2. Complete Entity-Relationship Model (Part 6 Requirements)

The unified data model defines 24 first-class entities spanning the entire lifecycle from ingestion to validated memory:

```
+----------------------------------------------------------------------------------------------------+
|                                    AXION ENTITY-RELATIONSHIP TOPOLOGY                              |
+----------------------------------------------------------------------------------------------------+
| [User] 1:N [Workspace] 1:N [Project] 1:N [Investigation]                                           |
|                                                                                                    |
| [Project] 1:N [Document] 1:N [DocumentChunk] 1:1 [ChunkEmbedding]                                 |
|                                     | 1:N                                                          |
|                                     v                                                              |
| [Domain] 1:N [Concept] 1:N [KGNode] 1:N [KGEdge] 1:N [EdgeProvenance]                             |
|                                |           |                                                       |
|                                v           v                                                       |
|                       [Fact] [Relationship] [Evidence] [Citation]                                  |
|                                                                                                    |
| [Investigation] 1:N [Problem] 1:1 [ReasoningDAG] 1:N [ReasoningStep]                               |
|                                                      | 1:N                                         |
|                                                      v                                             |
|                                          [Assumption] & [Constraint]                               |
|                                                      |                                             |
|                                                      v                                             |
| [CompositionRecord] <----> [TransferRecord] <----> [Hypothesis]                                    |
|                                                         | 1:N                                      |
|                                                         v                                          |
|                                                    [Experiment]                                    |
|                                                         | 1:1                                      |
|                                                         v                                          |
|                                                 [ValidationResult]                                 |
|                                                         | 1:1                                      |
|                                                         v                                          |
|                                                   [MemoryRecord]                                   |
+----------------------------------------------------------------------------------------------------+
```

---

## 3. Entity Specifications (The 24 Core Data Entities)

```
+-------------------+-------------------------------------------------------------------------------------------------------------------+
| ENTITY NAME       | PURPOSE, KEY FIELDS, PROVENANCE & VALIDATION STATUS                                                                |
+-------------------+-------------------------------------------------------------------------------------------------------------------+
| 1. User           | System user profile, authentication identity, role (Admin, Researcher, Student, Guest). Fields: id, email,        |
|                   | hashed_password, role, created_at.                                                                                |
+-------------------+-------------------------------------------------------------------------------------------------------------------+
| 2. Workspace      | Multi-tenant boundary. Enforces strict data isolation. Fields: id, user_id, name, created_at.                     |
+-------------------+-------------------------------------------------------------------------------------------------------------------+
| 3. Project        | Research topic container (e.g. "Solar EV Design", "Solid-State Batteries"). Fields: id, workspace_id, title, desc. |
+-------------------+-------------------------------------------------------------------------------------------------------------------+
| 4. Document       | Ingested file or resource registry. Fields: id, project_id, title, source_type (PDF, Web, API), file_hash_sha256, |
|                   | trust_tier (PEER_REVIEWED, TECHNICAL_DOC, PUBLIC_WEB), license_type. Provenance: source_uri, ingestion_timestamp. |
+-------------------+-------------------------------------------------------------------------------------------------------------------+
| 5. Source         | Catalog of external knowledge providers. Fields: id, name, base_url, source_category, trust_rating, api_auth_type.|
+-------------------+-------------------------------------------------------------------------------------------------------------------+
| 6. Domain         | Scientific or technical discipline namespace. Fields: id, namespace (e.g. "physics:thermo", "eng:electrical"),   |
|                   | description, parent_domain_id.                                                                                    |
+-------------------+-------------------------------------------------------------------------------------------------------------------+
| 7. Concept        | Normalized canonical scientific concept. Fields: id, domain_id, canonical_name, symbol, si_unit, description.     |
+-------------------+-------------------------------------------------------------------------------------------------------------------+
| 8. Entity         | Named instances of concepts in documents (e.g. "LiFePO4", "0.8 m^2 PV Array"). Fields: id, concept_id, label.    |
+-------------------+-------------------------------------------------------------------------------------------------------------------+
| 9. Fact           | Documented empirical truth with page coordinates. Fields: id, document_id, chunk_id, statement, epistemic_tier=1. |
+-------------------+-------------------------------------------------------------------------------------------------------------------+
| 10. Relationship  | Attributed directed connection between two concepts. Fields: id, source_concept_id, target_concept_id, relation_type.|
+-------------------+-------------------------------------------------------------------------------------------------------------------+
| 11. Evidence      | Verifiable textual or tabular snippet supporting a fact or edge. Fields: id, chunk_id, snippet_text, bounding_box.|
+-------------------+-------------------------------------------------------------------------------------------------------------------+
| 12. Citation      | Formatted bibliographic reference linking a statement to exact page coordinates. Fields: id, doc_id, page_no, bbox|
+-------------------+-------------------------------------------------------------------------------------------------------------------+
| 13. KGNode        | Knowledge Graph entity node. Fields: id, canonical_name, domain_namespace, category, symbol, si_dimension, attrs.|
+-------------------+-------------------------------------------------------------------------------------------------------------------+
| 14. KGEdge        | Knowledge Graph relation edge. Fields: id, source_node_id, target_node_id, relation_type, epistemic_tier, conf.   |
+-------------------+-------------------------------------------------------------------------------------------------------------------+
| 15. Problem       | Formal user research/engineering goal. Fields: id, investigation_id, goal_statement, target_variables, constraints.|
+-------------------+-------------------------------------------------------------------------------------------------------------------+
| 16. ReasoningStep | An individual sub-goal or deduction in a reasoning DAG. Fields: id, dag_id, step_order, node_type, content, tier.|
+-------------------+-------------------------------------------------------------------------------------------------------------------+
| 17. Composition   | Full audit trail of multi-domain variable harmonization and equation coupling. Fields: id, investigation_id,       |
|     Record        | source_domains, unified_variables, composed_equations_latex, dimensional_homogeneity_passed (bool).               |
+-------------------+-------------------------------------------------------------------------------------------------------------------+
| 18. Transfer      | Full audit trail of cross-domain structural mapping. Fields: id, source_domain, target_domain, structural_morphism,|
|     Record        | applicability_verdict (ACCEPT/REJECT), violated_assumption, transfer_explanation.                                 |
+-------------------+-------------------------------------------------------------------------------------------------------------------+
| 19. Assumption    | Underlying condition required for a law or transfer to hold (e.g. "laminar_flow", "linear_elasticity"). Fields:   |
|                   | id, statement, domain_id, is_active (bool), validation_state (VERIFIED, UNVERIFIED, VIOLATED).                     |
+-------------------+-------------------------------------------------------------------------------------------------------------------+
| 20. Constraint    | Physical or operational bound (e.g. "P_max <= 350 W", "T >= 0 K"). Fields: id, variable_symbol, lower_bound, upper.|
+-------------------+-------------------------------------------------------------------------------------------------------------------+
| 21. Hypothesis    | Structured testable conjecture. Fields: id, premise, mechanism, prediction, counter_evidence, validation_status.  |
+-------------------+-------------------------------------------------------------------------------------------------------------------+
| 22. Experiment    | Computational execution specification. Fields: id, hypothesis_id, script_type (Python, SymPy), generated_code.   |
+-------------------+-------------------------------------------------------------------------------------------------------------------+
| 23. Validation    | Sandbox execution output. Fields: id, experiment_id, exit_code, stdout, stderr, execution_duration_ms, verdict.  |
+-------------------+-------------------------------------------------------------------------------------------------------------------+
| 24. MemoryRecord  | Immutable verified finding ledger item. Fields: id, hypothesis_id, finding_statement, boundary_envelope (JSONB),  |
|                   | content_hash_sha256, version_number.                                                                              |
+-------------------+-------------------------------------------------------------------------------------------------------------------+
```

---

## 4. Deep Inspection Capabilities: Composition & Transfer Audit Trails

To satisfy Part 6 ("We must be able to inspect which original knowledge was used, which domains it came from, why concepts were connected, how knowledge was composed, what was transferred, under what conditions, which assumptions were made, and how the result was validated"), AXION models the `CompositionRecord` and `TransferRecord` as first-class queryable relational objects:

### 4.1 SQL Schema for Inspection Records

```sql
-- Full inspection audit trail for multi-domain composition
CREATE TABLE composition_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    investigation_id UUID NOT NULL REFERENCES investigations(id) ON DELETE CASCADE,
    participating_domains JSONB NOT NULL, -- e.g. ["physics:photovoltaics", "eng:mechanical_kinematics", "eng:electrical_powertrain"]
    input_chunk_ids UUID[] NOT NULL,      -- Array of original primary evidence chunks used
    unified_variable_registry JSONB NOT NULL, -- {"v": {"name": "velocity", "si_unit": "m/s", "source_doc": "doc-uuid-1"}}
    composed_governing_equations JSONB NOT NULL, -- Array of LaTeX equations representing coupled system
    dimensional_balance_verified BOOLEAN NOT NULL DEFAULT FALSE,
    sympy_reduction_log TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Full inspection audit trail for cross-domain analogical transfer
CREATE TABLE transfer_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    composition_record_id UUID REFERENCES composition_records(id),
    source_domain VARCHAR(64) NOT NULL,   -- e.g. "fluid_dynamics"
    target_domain VARCHAR(64) NOT NULL,   -- e.g. "electrical_kinematics"
    source_principle_id UUID REFERENCES graph_nodes(id),
    structural_morphism JSONB NOT NULL,  -- e.g. {"ΔP": "V", "Q": "I", "R_h": "R_e"}
    assumptions_evaluated JSONB NOT NULL, -- e.g. [{"assumption": "laminar_flow", "target_state": "SATISFIED", "proof": "Re < 2000"}]
    applicability_verdict VARCHAR(32) NOT NULL, -- 'ACCEPTED', 'REJECTED', 'FLAGGED_ASSUMPTION'
    rejection_explanation TEXT,           -- Explanation of physical violation if rejected
    human_readable_rationale TEXT NOT NULL, -- Clear explanation of WHY the connection was made
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

---

## 5. Complete Relational DDL & Indices

```sql
-- Enable Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- Workspaces & Multi-Tenancy
CREATE TABLE workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(128) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Documents & Provenance
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    source_type VARCHAR(32) NOT NULL,
    source_uri TEXT NOT NULL,
    file_hash_sha256 VARCHAR(64) UNIQUE NOT NULL,
    trust_tier VARCHAR(16) NOT NULL DEFAULT 'UNVERIFIED',
    license_type VARCHAR(64) DEFAULT 'UNKNOWN',
    page_count INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    page_number INTEGER NOT NULL,
    text_content TEXT NOT NULL,
    token_count INTEGER NOT NULL,
    structural_header TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_doc_chunk_idx UNIQUE (document_id, chunk_index)
);

CREATE TABLE document_bounding_boxes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chunk_id UUID NOT NULL REFERENCES document_chunks(id) ON DELETE CASCADE,
    page_number INTEGER NOT NULL,
    x0 NUMERIC(7, 2) NOT NULL,
    y0 NUMERIC(7, 2) NOT NULL,
    x1 NUMERIC(7, 2) NOT NULL,
    y1 NUMERIC(7, 2) NOT NULL
);

CREATE TABLE chunk_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chunk_id UUID NOT NULL UNIQUE REFERENCES document_chunks(id) ON DELETE CASCADE,
    embedding vector(1536),
    embedding_model VARCHAR(64) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_embeddings_hnsw ON chunk_embeddings 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Knowledge Graph
CREATE TABLE graph_nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    canonical_name VARCHAR(255) NOT NULL,
    domain_namespace VARCHAR(64) NOT NULL,
    category VARCHAR(32) NOT NULL,
    symbol VARCHAR(32),
    si_dimension VARCHAR(64),
    description TEXT,
    attributes JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_node_name_domain UNIQUE (canonical_name, domain_namespace)
);

CREATE INDEX idx_nodes_domain ON graph_nodes (domain_namespace);

CREATE TABLE graph_edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_node_id UUID NOT NULL REFERENCES graph_nodes(id) ON DELETE CASCADE,
    target_node_id UUID NOT NULL REFERENCES graph_nodes(id) ON DELETE CASCADE,
    relation_type VARCHAR(64) NOT NULL,
    epistemic_tier VARCHAR(32) NOT NULL DEFAULT 'FACT_DOCUMENTED',
    confidence NUMERIC(4, 3) NOT NULL DEFAULT 1.000,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_edges_src_rel ON graph_edges (source_node_id, relation_type);
CREATE INDEX idx_edges_tgt_rel ON graph_edges (target_node_id, relation_type);

CREATE TABLE edge_provenance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    edge_id UUID NOT NULL REFERENCES graph_edges(id) ON DELETE CASCADE,
    chunk_id UUID NOT NULL REFERENCES document_chunks(id) ON DELETE CASCADE,
    extracted_snippet TEXT NOT NULL,
    extraction_method VARCHAR(32) NOT NULL
);

-- Validated Findings Ledger
CREATE TABLE validated_findings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    finding_statement TEXT NOT NULL,
    governing_equation_latex TEXT,
    applicable_domain VARCHAR(64) NOT NULL,
    boundary_envelope JSONB NOT NULL,
    invariants_required JSONB NOT NULL,
    version_number INTEGER NOT NULL DEFAULT 1,
    content_hash_sha256 VARCHAR(64) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_val_findings_domain ON validated_findings (applicable_domain);
```
