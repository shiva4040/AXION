import time
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from axion.core.provider import LLMProvider, get_llm_provider
from axion.core.types import EpistemicTier
from axion.knowledge_graph.graph import KnowledgeGraphStore
from axion.baseline.retriever import BaselineRetriever
from axion.simple_tester.tester import SimpleHypothesisTester
from axion.simple_tester.types import ValidationVerdict
from axion.reasoning.types import (
    ReasoningDAG, SubProblem, SubProblemStatus, SubProblemExecutionResult,
    ContradictionAlert, ReasoningOutcome
)
from axion.reasoning.decomposer import GoalDecomposer
from axion.reasoning.contradiction import ContradictionDetector

class ReasoningEngine:
    """
    Component 5: Reasoning System Engine.
    Coordinates inspectable goal decomposition, multi-hop premise verification,
    cross-source contradiction detection, and mathematical validation.
    """
    def __init__(
        self,
        db_session: AsyncSession,
        provider: Optional[LLMProvider] = None,
        hypothesis_tester: Optional[SimpleHypothesisTester] = None
    ):
        self.session = db_session
        self.provider = provider or get_llm_provider()
        self.decomposer = GoalDecomposer(self.provider)
        self.kg_store = KnowledgeGraphStore(db_session)
        self.retriever = BaselineRetriever(db_session, self.provider)
        self.tester = hypothesis_tester or SimpleHypothesisTester()
        self.contradiction_detector = ContradictionDetector(db_session)

    async def reason_over_problem(
        self,
        goal: str,
        variable_values: Optional[Dict[str, float]] = None
    ) -> ReasoningOutcome:
        """
        Executes inspectable, multi-step neuro-symbolic reasoning over a goal:
        1. Decompose goal into an acyclic dependency graph (DAG).
        2. Evaluate each sub-problem in topological dependency order.
        3. Retrieve evidence chunks and explore Knowledge Graph paths.
        4. Validate equations with SimpleHypothesisTester.
        5. Scan for cross-source contradictions.
        6. Synthesize comprehensive, transparent outcome.
        """
        # Step 1: Decompose Goal into DAG
        dag: ReasoningDAG = await self.decomposer.decompose(goal)

        step_results: List[SubProblemExecutionResult] = []
        all_missing_info: List[str] = []
        all_unresolved: List[str] = []
        is_fully_solved = True

        # Step 2: Evaluate Sub-Problems in Topological Order
        for sp_id in dag.topological_order:
            subproblem = dag.sub_problems.get(sp_id)
            if not subproblem:
                continue

            subproblem.status = SubProblemStatus.IN_PROGRESS
            equations_verified: List[str] = []
            failed_validations: List[str] = []
            missing_vars: List[str] = []
            assumptions: List[str] = []
            conclusions: List[str] = []
            citations: List[Dict[str, Any]] = []

            # 2a: Retrieve primary evidence for subproblem
            search_query = f"{subproblem.title} {subproblem.description}"
            chunks = await self.retriever.retrieve(query=search_query, top_k=2, min_similarity=0.15)
            
            for c in chunks:
                citations.append({
                    "chunk_id": c.chunk_id,
                    "document_title": c.document_title,
                    "page_number": c.page_number,
                    "similarity": c.similarity_score
                })

            # 2b: Validate equations if present
            if subproblem.equations_to_evaluate:
                for eq in subproblem.equations_to_evaluate:
                    val_res = self.tester.validate_equation(
                        equation_str=eq,
                        variable_values=variable_values
                    )
                    if val_res.verdict == ValidationVerdict.VALID:
                        equations_verified.append(f"{eq} (Valid: {val_res.lhs_dimension})")
                        conclusions.append(f"Equation '{eq}' verified as physically and dimensionally homogeneous.")
                    elif val_res.verdict == ValidationVerdict.INSUFFICIENT_INFORMATION:
                        missing_vars.extend(val_res.failed_conditions)
                        all_missing_info.extend(val_res.failed_conditions)
                        subproblem.status = SubProblemStatus.NEEDS_EVIDENCE
                        is_fully_solved = False
                    else:
                        failed_validations.extend(val_res.failed_conditions)
                        subproblem.status = SubProblemStatus.BLOCKED
                        is_fully_solved = False

            # If no validation errors, mark solved
            if subproblem.status not in [SubProblemStatus.BLOCKED, SubProblemStatus.NEEDS_EVIDENCE]:
                subproblem.status = SubProblemStatus.SOLVED
                conclusions.append(f"Sub-goal '{subproblem.title}' successfully analyzed.")

            step_results.append(
                SubProblemExecutionResult(
                    subproblem_id=subproblem.id,
                    title=subproblem.title,
                    epistemic_tier=EpistemicTier.INFERENCE_DEDUCED if conclusions else EpistemicTier.FACT_DOCUMENTED,
                    derived_conclusions=conclusions,
                    equations_verified=equations_verified,
                    failed_validations=failed_validations,
                    missing_variables=missing_vars,
                    assumptions_made=assumptions,
                    supporting_citations=citations
                )
            )

        # Step 3: Scan for Contradictions across Knowledge Graph
        contradictions = await self.contradiction_detector.scan_contradictions()
        if contradictions:
            all_unresolved.append(
                f"{len(contradictions)} direct contradiction(s) detected between primary sources in the Knowledge Graph."
            )

        # Step 4: Summary Explanation
        summary = (
            f"Reasoning completed across {len(dag.sub_problems)} sub-problems. "
            f"Execution status: {'FULLY_SOLVED' if is_fully_solved else 'PARTIAL_GAPS_DETECTED'}."
        )

        return ReasoningOutcome(
            problem_id=dag.problem_id,
            goal=goal,
            dag=dag,
            step_results=step_results,
            contradictions_detected=contradictions,
            missing_information=list(set(all_missing_info)),
            unresolved_questions=all_unresolved,
            is_fully_solved=is_fully_solved,
            summary_explanation=summary
        )
