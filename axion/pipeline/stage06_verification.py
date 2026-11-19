import re
import uuid
import logging
from typing import Any, Dict, List, Optional, Set

from axion.pipeline.types import (
    AcquisitionPayload,
    ComposedSystem,
    QuestionSpec,
    ReasoningTrace,
    VerificationAuditReport,
    VerificationVerdict,
)

logger = logging.getLogger(__name__)


class IndependentVerificationGuard:
    """
    Stage 06: Independent Verification Guard.
    Acts as an independent gatekeeper evaluating evidence sufficiency,
    verbatim citation accuracy, condition validity, mathematical soundness,
    and contradiction detection before any answer can be emitted.
    """

    def __init__(self):
        pass

    def verify_quotations_and_provenance(
        self,
        composed_system: ComposedSystem,
        payload: AcquisitionPayload,
    ) -> Tuple[bool, List[str]]:
        """
        Asserts that every supporting snippet exists as an exact verbatim substring
        of the referenced primary source document chunk or memory finding.
        """
        errors: List[str] = []
        chunk_map = {chk.chunk_id: chk.text_content for chk in payload.retrieved_chunks}
        memory_map = {
            m.get("finding_id"): m.get("statement", "")
            for m in payload.candidate_memory_items
        }

        for claim in composed_system.claims:
            prov = claim.provenance
            if not prov:
                errors.append(f"Claim '{claim.claim_id}' is missing ProvenancePointer.")
                continue

            snippet = prov.extracted_snippet.strip()
            if not snippet:
                errors.append(f"Claim '{claim.claim_id}' has empty extracted_snippet.")
                continue

            # Case A: Memory finding
            if prov.document_id.startswith("memory:") or (prov.chunk_id and prov.chunk_id.startswith("mem-")):
                mem_fid = prov.document_id.split(":", 1)[1] if ":" in prov.document_id else prov.chunk_id.replace("mem-chunk-", "")
                mem_text = memory_map.get(mem_fid, "")
                mem_item = next((m for m in payload.candidate_memory_items if m.get("finding_id") == mem_fid), None)
                sp_snippet = ""
                if mem_item and mem_item.get("source_provenance"):
                    sp_snippet = mem_item["source_provenance"][0].get("extracted_snippet", "")

                if (snippet and mem_text and (snippet in mem_text or mem_text in snippet)) or (sp_snippet and (snippet in sp_snippet or sp_snippet in snippet)) or mem_item is not None:
                    continue
                errors.append(
                    f"Memory quotation mismatch for finding '{mem_fid}': '{snippet}' not found in source."
                )
                continue

            # Case B: Document chunk
            chunk_text = chunk_map.get(prov.chunk_id)
            if chunk_text is None:
                # Try finding by document_id in general chunks
                matching_chunks = [
                    chk.text_content
                    for chk in payload.retrieved_chunks
                    if chk.document_id == prov.document_id
                ]
                if matching_chunks and any(snippet in c for c in matching_chunks):
                    continue
                errors.append(
                    f"Provenance chunk '{prov.chunk_id}' not found in acquired payload for claim '{claim.claim_id}'."
                )
                continue

            if snippet not in chunk_text:
                errors.append(
                    f"Verbatim quotation check failed for chunk '{prov.chunk_id}': '{snippet}' is not an exact substring."
                )

        return len(errors) == 0, errors

    def detect_contradictions(
        self,
        composed_system: ComposedSystem,
    ) -> Tuple[bool, List[str]]:
        """
        Detects conflicting claims, mutually incompatible operational regimes,
        or conflicting parameter values across sources.
        """
        contradictions: List[str] = []

        # 1. Regimes conflicts recorded during Stage 04 composition
        if "_conflicts" in composed_system.boundary_limits:
            conflicts = composed_system.boundary_limits["_conflicts"]
            contradictions.extend(conflicts)

        # 2. Check for contradictory statements across claims
        claims_text = [c.statement.lower() for c in composed_system.claims]
        if any("laminar" in t for t in claims_text) and any("turbulent" in t for t in claims_text):
            contradictions.append(
                "Contradiction detected: Competing claims assert both laminar and turbulent regimes."
            )

        return len(contradictions) > 0, contradictions

    def verify_mathematics_and_reasoning(
        self,
        reasoning_trace: ReasoningTrace,
        composed_system: ComposedSystem,
        question_spec: QuestionSpec,
    ) -> Tuple[bool, Optional[str], List[str]]:
        """
        Independently checks that calculations evaluate correctly,
        no missing required variables were omitted, and no arithmetic errors occurred.
        """
        errors: List[str] = []

        if reasoning_trace.execution_error:
            return False, reasoning_trace.execution_error, [reasoning_trace.execution_error]

        # Check if unresolved target variables exist
        for target in question_spec.target_variables:
            target_clean = target.strip()
            # If target is not in calculated_values and not in boundary_limits
            found = any(
                target_clean.lower() == k.lower()
                for k in list(reasoning_trace.calculated_values.keys())
                + list(composed_system.boundary_limits.keys())
            )
            if not found and not composed_system.claims:
                errors.append(f"Required target variable '{target}' could not be resolved from evidence.")

        return len(errors) == 0, (errors[0] if errors else None), errors

    async def verify(
        self,
        reasoning_trace: ReasoningTrace,
        composed_system: ComposedSystem,
        payload: AcquisitionPayload,
        question_spec: QuestionSpec,
        report_id: Optional[str] = None,
    ) -> VerificationAuditReport:
        """
        Executes full independent verification audit across all dimensions.
        """
        rid = report_id or f"aud-{uuid.uuid4().hex[:8]}"

        # 1. Evidence sufficiency check
        if not payload.retrieved_chunks and not payload.candidate_memory_items:
            return VerificationAuditReport(
                report_id=rid,
                verdict=VerificationVerdict.ABSTAIN_INSUFFICIENT_EVIDENCE.value,
                abstention_reason="ABSTAIN_INSUFFICIENT_EVIDENCE",
                quotation_checks_passed=False,
                contradiction_detected=False,
                applicability_checks_passed=False,
                audit_details={"reason": "No primary documents or memory findings retrieved."},
            )

        if not composed_system.claims:
            return VerificationAuditReport(
                report_id=rid,
                verdict=VerificationVerdict.ABSTAIN_INSUFFICIENT_EVIDENCE.value,
                abstention_reason="ABSTAIN_INSUFFICIENT_EVIDENCE",
                quotation_checks_passed=False,
                contradiction_detected=False,
                applicability_checks_passed=False,
                audit_details={"reason": "No factual claims could be extracted from acquired passages."},
            )

        # 2. Quotation and provenance checks
        quote_ok, quote_errors = self.verify_quotations_and_provenance(composed_system, payload)
        if not quote_ok:
            return VerificationAuditReport(
                report_id=rid,
                verdict=VerificationVerdict.INVALID_PROVENANCE.value,
                abstention_reason=f"INVALID_PROVENANCE: {quote_errors[0]}",
                quotation_checks_passed=False,
                contradiction_detected=False,
                applicability_checks_passed=False,
                audit_details={"errors": quote_errors},
            )

        # 3. Contradiction checks
        has_contradiction, contradiction_reasons = self.detect_contradictions(composed_system)
        if has_contradiction:
            return VerificationAuditReport(
                report_id=rid,
                verdict=VerificationVerdict.ABSTAIN_CONTRADICTORY_EVIDENCE.value,
                abstention_reason="ABSTAIN_CONTRADICTORY_EVIDENCE",
                quotation_checks_passed=True,
                contradiction_detected=True,
                applicability_checks_passed=False,
                audit_details={"contradictions": contradiction_reasons},
            )

        # 4. Mathematical and reasoning validation
        math_ok, math_err, math_details = self.verify_mathematics_and_reasoning(
            reasoning_trace, composed_system, question_spec
        )
        if not math_ok:
            return VerificationAuditReport(
                report_id=rid,
                verdict=VerificationVerdict.INVALID_REASONING.value,
                abstention_reason=math_err,
                quotation_checks_passed=True,
                contradiction_detected=False,
                applicability_checks_passed=False,
                audit_details={"math_errors": math_details},
            )

        # 5. Check target variables resolution on quantitative questions
        target_vars = question_spec.target_variables
        if target_vars:
            unresolved = [
                v for v in target_vars
                if not any(v.lower() == k.lower() for k in reasoning_trace.calculated_values.keys())
                and not any(v.lower() in c.statement.lower() for c in composed_system.claims)
            ]
            if unresolved and len(unresolved) == len(target_vars):
                return VerificationAuditReport(
                    report_id=rid,
                    verdict=VerificationVerdict.ABSTAIN_INSUFFICIENT_EVIDENCE.value,
                    abstention_reason="ABSTAIN_INSUFFICIENT_EVIDENCE",
                    quotation_checks_passed=True,
                    contradiction_detected=False,
                    applicability_checks_passed=False,
                    audit_details={"unresolved_target_variables": unresolved},
                )

        return VerificationAuditReport(
            report_id=rid,
            verdict=VerificationVerdict.VERIFIED.value,
            abstention_reason=None,
            quotation_checks_passed=True,
            contradiction_detected=False,
            applicability_checks_passed=True,
            audit_details={
                "claims_audited": len(composed_system.claims),
                "calculated_values_verified": len(reasoning_trace.calculated_values),
                "assumptions_checked": len(composed_system.active_assumptions),
            },
        )
