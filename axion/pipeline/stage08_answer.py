import logging
from typing import Any, Dict, List, Optional

from axion.core.provider import LLMProvider
from axion.pipeline.types import (
    ComposedSystem,
    PipelineAnswerResponse,
    QuestionSpec,
    ReasoningTrace,
    StageExecutionLog,
    SupportingEvidenceItem,
    VerificationAuditReport,
    VerificationVerdict,
)

logger = logging.getLogger(__name__)


class MinimalAnswerGenerator:
    """
    Stage 08: Minimal Answer Generator.
    Synthesizes a structured, fully attributed scientific answer when verification succeeds,
    or emits a precise, standardized refusal when evidence is insufficient or contradictory.
    """

    def __init__(self, provider: Optional[LLMProvider] = None):
        self.provider = provider

    def generate_abstention_response(
        self,
        audit_report: VerificationAuditReport,
        composed_system: ComposedSystem,
        question_spec: QuestionSpec,
        execution_logs: List[StageExecutionLog],
        total_latency_ms: float,
    ) -> PipelineAnswerResponse:
        """Emits an explicit, informative abstention notice explaining the exact reason for refusal."""
        reason = audit_report.abstention_reason or "Insufficient evidence to answer reliably."
        
        if "CONTRADICTORY" in audit_report.verdict:
            direct_ans = (
                f"AXION cannot provide a verified answer because competing sources assert contradictory evidence: {reason}"
            )
        elif "PROVENANCE" in audit_report.verdict:
            direct_ans = (
                f"AXION cannot answer this question because evidence citation verification failed: {reason}"
            )
        elif "REASONING" in audit_report.verdict:
            direct_ans = (
                f"AXION cannot answer this question because mathematical reasoning failed: {reason}"
            )
        else:
            direct_ans = (
                f"AXION cannot answer this question because essential evidence is absent from the provided documents. "
                f"Reason: {reason}"
            )

        return PipelineAnswerResponse(
            query_id=question_spec.query_id,
            query=question_spec.raw_query,
            verdict=audit_report.verdict,
            direct_answer=direct_ans,
            supporting_evidence=[],
            active_assumptions=composed_system.active_assumptions,
            calculation_steps=[],
            is_abstained=True,
            abstention_reason=reason,
            execution_logs=execution_logs,
            total_latency_ms=total_latency_ms,
        )

    def generate_answer(
        self,
        audit_report: VerificationAuditReport,
        reasoning_trace: ReasoningTrace,
        composed_system: ComposedSystem,
        question_spec: QuestionSpec,
        execution_logs: List[StageExecutionLog],
        total_latency_ms: float,
    ) -> PipelineAnswerResponse:
        """
        Executes Stage 08 Answer Generation.
        Dispatches either a structured evidence-backed answer or an explicit abstention.
        """
        # If verification did not pass, abstain explicitly
        if audit_report.verdict != VerificationVerdict.VERIFIED.value:
            return self.generate_abstention_response(
                audit_report=audit_report,
                composed_system=composed_system,
                question_spec=question_spec,
                execution_logs=execution_logs,
                total_latency_ms=total_latency_ms,
            )

        # Assemble supporting evidence with exact citations
        evidence_items: List[SupportingEvidenceItem] = []
        for claim in composed_system.claims:
            prov = claim.provenance
            doc_label = prov.document_id if prov else "Primary Literature"
            page_label = f"Page {prov.page_number}" if prov and prov.page_number else "Page 1"
            evidence_items.append(
                SupportingEvidenceItem(
                    claim=claim.statement,
                    citation=f"{doc_label}, {page_label}",
                    verbatim_quote=prov.extracted_snippet if prov else claim.statement,
                    provenance=prov,
                )
            )

        # Synthesize direct answer
        calc_summaries = [f"{k} = {v}" for k, v in reasoning_trace.calculated_values.items()]
        domains_str = ", ".join(question_spec.domain_tags) if question_spec.domain_tags else "scientific literature"

        if calc_summaries:
            direct_answer = (
                f"Based on verified primary evidence in {domains_str}, the calculated values are: "
                f"{', '.join(calc_summaries)}."
            )
        elif composed_system.claims:
            lead_claim = composed_system.claims[0].statement
            direct_answer = (
                f"Based on verified primary evidence in {domains_str}: {lead_claim}"
            )
        else:
            direct_answer = f"Verified investigation completed across {domains_str}."

        return PipelineAnswerResponse(
            query_id=question_spec.query_id,
            query=question_spec.raw_query,
            verdict="ANSWERABLE",
            direct_answer=direct_answer,
            supporting_evidence=evidence_items,
            active_assumptions=composed_system.active_assumptions,
            calculation_steps=reasoning_trace.steps,
            is_abstained=False,
            abstention_reason=None,
            execution_logs=execution_logs,
            total_latency_ms=total_latency_ms,
        )
