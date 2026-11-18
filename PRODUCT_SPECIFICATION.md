# AXION — Product Specification Document

**Document Version:** 2.0.0  
**Date:** November 18, 2026  
**Status:** Approved for Phase 0 Specification  
**Project:** AXION — Universal Knowledge and Cross-Domain Intelligence Platform  

---

## 1. Product Overview, Scope & Universal Knowledge Domains

### 1.1 Product Mission
AXION is a universal knowledge and cross-domain problem-solving platform. It is engineered to help human investigators understand complex subjects, learn new concepts, connect information across disciplines, solve technical and scientific problems, and build practical solutions backed by verifiable evidence and empirical validation.

### 1.2 Universal Domain Scope (Part 1.2 Requirements)
AXION is explicitly **not restricted to a narrow scientific subfield**. It supports knowledge representation, composition, and transfer across:

- **Physical & Natural Sciences:** Physics (Classical, Quantum, Thermodynamics), Chemistry (Inorganic, Organic, Physical), Biology (Molecular, Cellular, Ecology), Materials Science.
- **Formal Sciences:** Mathematics, Statistics, Computer Science, Artificial Intelligence, Information Theory.
- **Engineering Disciplines:** Electrical, Mechanical, Civil, Chemical, Aerospace, Biomedical, Systems Engineering.
- **Health & Life Sciences:** Medicine, Pharmacology, Public Health, Physiology, Genetics.
- **Social & Economic Sciences:** Economics, Business Logistics, System Dynamics, Organizational Theory.
- **Humanities & General Knowledge:** History of Technology, Scientific Methodology, Philosophy of Science, Education.

---

## 2. Core User Problems & Product Solutions

```
+-------------------------------------------------------------+---------------------------------------------------------------+
| USER PROBLEM                                                | HOW AXION SOLVES IT                                           |
+-------------------------------------------------------------+---------------------------------------------------------------+
| 1. Disciplinary Silos: Solutions require knowledge across   | Cross-Domain Engine identifies structural analogies and       |
|    multiple fields, but users only master one or two.       | composes multi-disciplinary equations into a unified model.   |
+-------------------------------------------------------------+---------------------------------------------------------------+
| 2. Hallucinatory RAG: Standard AI tools invent plausible    | Strict Epistemic Ladder (Tiers 1-4) with verifiable bounding- |
|    citations and generate ungrounded formulas.              | box coordinates and NLI entailment checking.                  |
+-------------------------------------------------------------+---------------------------------------------------------------+
| 3. Lack of Physical Grounding: AI models cannot tell if an   | Deterministic symbolic unit analysis (SymPy) and isolated     |
|    equation violates conservation laws or physical bounds.  | Docker container simulations verify solutions before output.  |
+-------------------------------------------------------------+---------------------------------------------------------------+
| 4. Unstructured Practical Guidance: AI chatbots output text | Generates hierarchical reasoning DAGs with explicit premises, |
|    summaries rather than actionable build instructions.     | equations, bill-of-materials, and step-by-step assembly guides.|
+-------------------------------------------------------------+---------------------------------------------------------------+
| 5. Amnesia & Fragile Context: Past discoveries are forgotten| Validated Knowledge Memory stores verified findings with      |
|    or misapplied to invalid downstream contexts.            | cryptographic hashes and operational boundary envelopes.       |
+-------------------------------------------------------------+---------------------------------------------------------------+
```

---

## 3. The 11 Unified Research Workspace Sections (Part 11 Requirements)

AXION breaks away from the generic conversational chatbot window, providing 11 specialized, interactive workspace sections within a unified research cockpit:

```
+------------------------------------+----------------------------------------------------------------------------------------------------+
| WORKSPACE SECTION                  | PURPOSE, PRIMARY VIEWS & USER CAPABILITIES                                                         |
+------------------------------------+----------------------------------------------------------------------------------------------------+
| 1. Home                            | Active investigation overview, pinned research projects, recent validation runs, system health.     |
+------------------------------------+----------------------------------------------------------------------------------------------------+
| 2. Research Workspace              | Central project cockpit: active query input, domain selector, project notes, goal formulation.     |
+------------------------------------+----------------------------------------------------------------------------------------------------+
| 3. Knowledge Explorer              | Interactive 2D/3D force-directed Knowledge Graph (Cytoscape.js), domain cluster filters, node and  |
|                                    | edge inspector, source provenance popup with page snippets.                                        |
+------------------------------------+----------------------------------------------------------------------------------------------------+
| 4. Cross-Domain Intelligence       | Dual-domain alignment canvas, structural analogy matrix, transfer mapping inspector, and formal   |
|                                    | Applicability Guard checklist (verifying underlying physical assumptions).                         |
+------------------------------------+----------------------------------------------------------------------------------------------------+
| 5. Research Assistant (Baseline)   | Conventional RAG chat interface with chunk citation cards. Operates strictly as the experimental   |
|                                    | control baseline for quick factual lookups.                                                        |
+------------------------------------+----------------------------------------------------------------------------------------------------+
| 6. Problem Solver                  | Hierarchical reasoning DAG explorer, mathematical derivation steps, constraint solver canvas,      |
|                                    | bill-of-materials generator, and step-by-step practical build guides.                              |
+------------------------------------+----------------------------------------------------------------------------------------------------+
| 7. Hypothesis Lab                  | Deck of structured hypothesis cards (Premise, Mechanism, Prediction, Counter-evidence, Test Plan), |
|                                    | uncertainty calibration sliders, and automated test script generator.                              |
+------------------------------------+----------------------------------------------------------------------------------------------------+
| 8. Experiment & Validation         | Containerized Python execution console, Monaco code editor, interactive Matplotlib/Plotly curves,   |
|                                    | stdout/stderr stream viewers, and simulation parameter sweeps.                                     |
+------------------------------------+----------------------------------------------------------------------------------------------------+
| 9. Validated Memory                | Searchable, immutable ledger of verified laws and findings, operational boundary envelope inspector|
|                                    | (T_range, P_max, materials), version history, and contextual re-applicability checker.             |
+------------------------------------+----------------------------------------------------------------------------------------------------+
| 10. Sources & Evidence             | Document manager: PDF viewer with coordinate bounding-box highlight overlays, web crawler status, |
|                                    | API feed monitor, license tracker, and trust-tier rating badges.                                   |
+------------------------------------+----------------------------------------------------------------------------------------------------+
| 11. Settings & Benchmarks          | LLM provider configuration (API keys, models), compute quotas, Docker sandbox security monitors,   |
|                                    | and real-time automated benchmark dashboard (evaluating all 15 metrics).                           |
+------------------------------------+----------------------------------------------------------------------------------------------------+
```

---

## 4. End-to-End User Journeys

### User Journey 1: Complex Engineering Design (Solar EV Powertrain)
1. **User Request:** User navigates to `Problem Solver` and inputs: *"Design a solar-powered commuter vehicle with a 75 kg payload, 25 km/h cruising speed, under 1000 W/m² solar insolation."*
2. **Domain Discovery:** AXION identifies required domains: Photovoltaics (Physics), Aerodynamics & Rolling Dynamics (Mechanical), Power Electronics & Motors (Electrical).
3. **Retrieval & Graph Ingestion:** Ingests solar cell specs (21% efficiency), aerodynamic drag constants, and motor efficiency curves into the Knowledge Graph.
4. **Knowledge Composition:** Composes road-load kinematics with photovoltaic power equations:
   $$P_{\text{solar}} = \text{Area} \cdot G \cdot \eta_{\text{pv}} \quad \text{vs.} \quad P_{\text{demand}} = \frac{(C_{rr} m g + \frac{1}{2}\rho C_d A_f v^2) v}{\eta_{\text{motor}}}$$
5. **Feasibility Deficit & Analogy Transfer:** Simple Tester checks SI units (Watts) and flags an energy deficit of 42 W for continuous driving. The Cross-Domain Engine transfers the concept of *hydraulic accumulator / grid buffer storage* to an electrical battery buffer.
6. **Simulation & Validation:** Full Tester runs a numerical simulation in the Docker sandbox, optimizing battery buffer capacity (240 Wh LiFePO4).
7. **Actionable Presentation:** Problem Solver outputs the complete bill of materials, circuit schematic, KaTeX derivations, and step-by-step build instructions with verified citations.

### User Journey 2: Interdisciplinary Scientific Discovery
1. **Literature Ingestion:** Researcher uploads 10 papers on high-entropy alloy corrosion in marine environments to `Sources & Evidence`.
2. **Knowledge Graph Exploration:** In `Knowledge Explorer`, researcher views the extracted network of crystal lattice configurations, passive film thicknesses, and pitting corrosion rates.
3. **Cross-Domain Analogy:** In `Cross-Domain Intelligence`, AXION detects a structural analogy between passive oxide film breakdown and dielectric breakdown in solid-state capacitors.
4. **Hypothesis Formulation:** `Hypothesis Lab` formulates a testable hypothesis: *Corrosion pitting initiation is governed by local dielectric breakdown of the passive layer induced by chloride ion tunneling under critical electrostatic gradients.*
5. **Memory Archival:** Following simulation validation, the finding is archived in `Validated Memory` with an explicit operational envelope ($T \in [273, 350]\text{ K}$, $[Cl^-] \le 2.0\text{ M}$).

---

## 5. Security, High-Risk Safety & Physical Safeguards (Part 10 Requirements)

Because AXION provides actionable, real-world instructions:
1. **High-Risk Physical Safety Filter:** Prompts requesting instructions for dangerous, toxic, or explosive materials (e.g., chemical synthesis of toxic agents, high-voltage bypasses, structural demolition) are intercepted by a safety classifier.
2. **Mandatory Safety Factors ($SF$):** All mechanical, structural, and electrical designs must calculate and specify an explicit engineering safety factor ($SF \ge 1.5$ structural, $SF \ge 2.0$ electrical/pressure).
3. **Epistemic Disclaimers on Physical Builds:** Outputs involving physical fabrication explicitly mandate certified lab supervision and state:
   > *"Computationally verified in simulation. Physical implementation requires licensed professional engineering verification."*
4. **Copyright & Licensing Hygiene:** Ingested documents are checked for open licenses (CC-BY, MIT, Public Domain). Restricted content is used strictly for extraction of factual data under fair-use principles, with full attribution and no unauthorized redistribution of primary text blocks.
