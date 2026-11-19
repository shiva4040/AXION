import uuid
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from axion.core.types import EpistemicTier, ProvenancePointer
from axion.knowledge_memory.memory import ValidatedKnowledgeMemory
from axion.knowledge_memory.types import KnowledgeStatus, ValidatedFinding
from axion.pipeline.types import (
    ComposedSystem,
    QuestionSpec,
    ReasoningTrace,
    VerificationAuditReport,
    VerificationVerdict,
)

logger = logging.getLogger(__name__)


class VerifiedMemoryManager:
    """
    Stage 07: Verified Findings Memory Manager.
    Manages reading of candidate findings and writing of newly verified knowledge.
    Enforces strict verification gating: unverified, rejected, or abstained conclusions
    are strictly barred from entering the validated knowledge memory.
    """

    def __init__(self, memory: Optional[ValidatedKnowledgeMemory] = None):
        self.memory = memory

    def read_candidate_findings(
        self,
        question_spec: QuestionSpec,
    ) -> List[Dict[str, Any]]:
        """
        Retrieves active verified findings from memory matching question concepts or domains.
        """
        if not self.memory:
            return []

        try:
            active_findings = self.memory.list_findings(active_only=True)
            matched: List[Dict[str, Any]] = []

            concepts_lower = [c.lower() for c in question_spec.extracted_concepts]
            domains_lower = [d.lower() for d in question_spec.domain_tags]

            for f in active_findings:
                text = f"{f.title} {f.statement}".lower()
                domain_match = any(d in text for d in domains_lower)
                concept_match = any(c in text for c in concepts_lower)
                if domain_match or concept_match:
                    matched.append({
                        "finding_id": f.finding_id,
                        "title": f.title,
                        "statement": f.statement,
                        "epistemic_tier": f.epistemic_tier.value if hasattr(f.epistemic_tier, "value") else str(f.epistemic_tier),
                        "active_assumptions": f.active_assumptions,
                        "applicable_conditions": f.applicable_conditions,
                        "limitations": f.limitations,
                        "source_provenance": [
                            p.model_dump() if hasattr(p, "model_dump") else dict(p)
                            for p in f.source_provenance
                        ],
                    })

            return matched
        except Exception as e:
            logger.warning("Error reading candidate memory findings: %s", e)
            return []

    def store_verified_finding(
        self,
        audit_report: VerificationAuditReport,
        reasoning_trace: ReasoningTrace,
        composed_system: ComposedSystem,
        question_spec: QuestionSpec,
    ) -> Optional[ValidatedFinding]:
        """
        Stores a new verified finding in memory ONLY if verification passed with VERIFIED.
        Rejects unverified, abstained, or invalid conclusions.
        """
        if not self.memory:
            return None

        # Mandatory Gatekeeper Rule: ONLY store if strictly VERIFIED
        if audit_report.verdict != VerificationVerdict.VERIFIED.value:
            logger.info(
                "Memory write-back skipped: audit verdict '%s' is not VERIFIED.",
                audit_report.verdict,
            )
            return None

        now = datetime.now(timezone.utc).isoformat()
        
        # Build finding statement from reasoning conclusions
        statement_parts = []
        for k, v in reasoning_trace.calculated_values.items():
            statement_parts.append(f"{k} = {v}")
        for p in reasoning_trace.inferred_premises[:2]:
            statement_parts.append(p)
        
        finding_statement = "; ".join(statement_parts)
        if not finding_statement:
            finding_statement = f"Verified finding for query: {question_spec.raw_query}"

        # Duplicate check: check if finding with identical statement already exists
        existing = self.memory.list_findings(active_only=True)
        for ef in existing:
            if ef.statement.strip().lower() == finding_statement.strip().lower():
                logger.info("Duplicate finding already in memory ('%s'). Skipping write.", ef.finding_id)
                return ef

        # Provenance gathering
        provenance_list: List[ProvenancePointer] = []
        for c in composed_system.claims:
            if c.provenance:
                provenance_list.append(c.provenance)

        fid = f"FIND-AUTOGEN-{uuid.uuid4().hex[:8]}"
        title_summary = question_spec.target_variables[0] if question_spec.target_variables else question_spec.raw_query[:40]
        domain_summary = ", ".join(question_spec.domain_tags) if question_spec.domain_tags else "General"
        finding = ValidatedFinding(
            finding_id=fid,
            version=1,
            title=f"Verified Finding: {title_summary} [{domain_summary}]",
            statement=finding_statement,
            status=KnowledgeStatus.VALID,
            hypothesis_id=f"hypo-{question_spec.query_id}",
            epistemic_tier=EpistemicTier.FINDING_VALIDATED,
            supporting_experiment_ids=[audit_report.report_id],
            source_provenance=provenance_list,
            active_assumptions=composed_system.active_assumptions,
            applicable_conditions=[c for clm in composed_system.claims for c in clm.conditions],
            created_at=now,
            updated_at=now,
        )

        try:
            self.memory._findings[finding.finding_id] = finding
            self.memory._audit_log[finding.finding_id] = []
            if self.memory.persistence_path:
                self.memory._save_to_disk()
            logger.info("Successfully stored verified finding '%s' in memory.", finding.finding_id)
            return finding
        except Exception as e:
            logger.error("Failed to store verified finding in memory: %s", e)
            return None
