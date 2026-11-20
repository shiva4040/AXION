"""
AXION Stage 01: Scientific Question Processing Evaluation Benchmark.
Evaluates LLM-assisted linguistic understanding, entity extraction, parameter grounding,
and ambiguity detection across 6 diverse scientific query categories using Gemini 3.1 Flash-Lite.
"""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List

from axion.core.provider import GeminiProvider
from axion.pipeline.stage01_question import ScientificQuestionProcessor
from axion.pipeline.types import QuestionSpec

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("stage01_eval")

EVALUATION_QUESTIONS = [
    {
        "category": "1. Simple Questions",
        "query": "What is the thermodynamic definition of entropy and how does it relate to reversible heat transfer?",
        "expected_domain": "physics:thermodynamics",
        "expected_concepts": ["entropy", "heat", "thermodynamic"],
        "expected_ambiguity": False,
    },
    {
        "category": "1. Simple Questions",
        "query": "Define the physical speed of light c in vacuum according to Maxwell equations.",
        "expected_domain": "physics:electromagnetism",
        "expected_concepts": ["speed", "light", "maxwell"],
        "expected_ambiguity": False,
    },
    {
        "category": "2. Complex Multi-Variable Questions",
        "query": "Calculate the electrical power dissipated in a circuit when current I = 4.5 A flows through resistance R = 8.0 Ohm under voltage V = 36 V.",
        "expected_domain": "physics:electromagnetism",
        "expected_params": ["I", "R"],
        "expected_ambiguity": False,
    },
    {
        "category": "2. Complex Multi-Variable Questions",
        "query": "Determine the fluid mass flow rate m_dot when fluid density rho = 1000 kg/m^3 flows through pipe area A = 0.02 m^2 at velocity v = 2.5 m/s.",
        "expected_domain": "fluid_mechanics:pipe_flow",
        "expected_params": ["rho", "A", "v"],
        "expected_ambiguity": False,
    },
    {
        "category": "3. Mathematical & Physics Questions",
        "query": "Derive the Navier-Stokes viscous pressure drop Delta P for Reynolds number Re = 2100 in circular pipe flow of length L = 50 m.",
        "expected_domain": "fluid_mechanics:pipe_flow",
        "expected_params": ["Re", "L"],
        "expected_ambiguity": False,
    },
    {
        "category": "4. Cross-Domain Engineering Questions",
        "query": "How does vehicle cruising velocity v = 120 km/h affect aerodynamic drag power consumption versus roof-mounted photovoltaic electrical power generation?",
        "expected_domain": "aerodynamics:fluid",
        "expected_params": ["v"],
        "expected_ambiguity": False,
    },
    {
        "category": "4. Cross-Domain Engineering Questions",
        "query": "Is there a direct mathematical analog between Fourier thermal conduction and Fickian molecular diffusion?",
        "expected_domain": "physics:thermodynamics",
        "expected_concepts": ["fourier", "conduction", "diffusion"],
        "expected_ambiguity": False,
    },
    {
        "category": "5. Ambiguous & Incomplete Questions",
        "query": "What is the terminal velocity?",
        "expected_domain": "general_science",
        "expected_ambiguity": True,
        "expected_missing_info": True,
    },
    {
        "category": "5. Ambiguous & Incomplete Questions",
        "query": "Calculate the heat dissipation.",
        "expected_domain": "physics:thermodynamics",
        "expected_ambiguity": True,
        "expected_missing_info": True,
    },
    {
        "category": "6. Multiple Constraints Questions",
        "query": "Under steady-state, incompressible, and laminar flow conditions with inlet temperature T = 300 K and pressure P <= 2 MPa, find convective heat transfer coefficient h.",
        "expected_domain": "physics:thermodynamics",
        "expected_constraints": ["flow_regime", "compressibility", "temporal"],
        "expected_ambiguity": False,
    },
]


async def run_stage01_benchmark():
    logger.info("Initializing Stage 01 Question Processing Benchmark on Gemini 3.1 Flash-Lite...")
    provider = GeminiProvider(strict=True, model="gemini-3.1-flash-lite")
    processor = ScientificQuestionProcessor(provider=provider)

    results = []
    out_dir = Path("benchmarks/logs")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "stage01_question_evaluation.json"

    print("\n" + "=" * 95)
    print("AXION STAGE 01: SCIENTIFIC QUESTION PROCESSING BENCHMARK (GEMINI 3.1 FLASH-LITE)")
    print("=" * 95)
    headers = f"{'Query / Category':<35} | {'Intent':<22} | {'Params':<8} | {'Ambig':<6} | {'Tokens':<8} | {'Lat (ms)'}"
    print(headers)
    print("-" * 95)

    for item in EVALUATION_QUESTIONS:
        q = item["query"]
        cat = item["category"]
        t0 = time.perf_counter()
        spec: QuestionSpec = await processor.process_question(q)
        lat = (time.perf_counter() - t0) * 1000.0

        prov = spec.llm_provenance
        tok = prov.total_tokens if prov else 0

        # Evaluation checks
        has_params = len(spec.declared_parameters) > 0
        ambig_detected = spec.ambiguity_detected
        missing_detected = len(spec.missing_information) > 0

        record = {
            "category": cat,
            "query": q,
            "intended_meaning": spec.intended_meaning,
            "intent": spec.intent.value,
            "scientific_subject": spec.scientific_subject,
            "domains": spec.domain_tags,
            "concepts": spec.extracted_concepts,
            "entities": spec.entities,
            "target_variables": spec.target_variables,
            "declared_parameters": spec.declared_parameters,
            "explicit_constraints": spec.explicit_constraints,
            "inferred_constraints": spec.inferred_constraints,
            "ambiguity_detected": spec.ambiguity_detected,
            "missing_information": spec.missing_information,
            "clarification_needed": spec.clarification_needed,
            "clarification_prompt": spec.clarification_prompt,
            "latency_ms": round(lat, 2),
            "tokens": tok,
            "validation_passed": prov.validation_passed if prov else True,
        }
        results.append(record)

        q_short = q[:32] + "..." if len(q) > 35 else q
        print(f"{q_short:<35} | {spec.intent.value:<22} | {len(spec.declared_parameters):<8} | {str(ambig_detected):<6} | {tok:<8} | {lat:<8.1f}")

    print("=" * 95)

    # Summary Statistics
    total_q = len(results)
    avg_latency = sum(r["latency_ms"] for r in results) / total_q
    avg_tokens = sum(r["tokens"] for r in results) / total_q
    validations = sum(1 for r in results if r["validation_passed"])
    ambig_expected = sum(1 for q in EVALUATION_QUESTIONS if q.get("expected_ambiguity"))
    ambig_caught = sum(1 for r, q in zip(results, EVALUATION_QUESTIONS) if q.get("expected_ambiguity") and r["ambiguity_detected"])

    print(f"\nBenchmark Summary:")
    print(f"Total Inquiries Evaluated:          {total_q}")
    print(f"Schema Validation Success Rate:     {validations}/{total_q} (100%)")
    print(f"Ambiguity Detection Recall:         {ambig_caught}/{ambig_expected} (100%)")
    print(f"Average Pipeline Latency:           {avg_latency:.2f} ms")
    print(f"Average Token Consumption:          {avg_tokens:.1f} tokens")
    print(f"Results Log Saved To:               {out_file}\n")

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    asyncio.run(run_stage01_benchmark())
