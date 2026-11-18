import uuid
from collections import deque
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple
from axion.core.types import EpistemicTier
from axion.hypothesis_tester.types import ExperimentRecord, ExperimentVerdict
from axion.knowledge_memory.types import (
    DependentImpactReport,
    FindingVersionRecord,
    KnowledgeStatus,
    ValidatedFinding,
)

class InvalidPromotionError(Exception):
    """Raised when an unverified or rejected hypothesis is promoted to validated knowledge."""
    pass

class FindingNotFoundError(Exception):
    """Raised when a specified finding ID cannot be located."""
    pass

class ValidatedKnowledgeMemory:
    """
    Component 9: Validated Knowledge Memory.
    Manages scientifically validated findings (Epistemic Tier 4: FINDING_VALIDATED).
    Enforces strict experimental promotion gates, immutable version history,
    explicit invalidation/superseding, and cascading dependency impact analysis.
    """

    def __init__(self):
        # finding_id -> ValidatedFinding
        self._findings: Dict[str, ValidatedFinding] = {}
        # finding_id -> List[FindingVersionRecord] (immutable audit log)
        self._audit_log: Dict[str, List[FindingVersionRecord]] = {}
        # dependency graph: parent_finding_id -> Set[child_finding_ids]
        self._downstream_dependents: Dict[str, Set[str]] = {}

    def store_validated_finding(
        self,
        finding: ValidatedFinding,
        experiment_record: Optional[ExperimentRecord] = None,
    ) -> ValidatedFinding:
        """
        Stores a new validated finding.
        Enforces the Epistemic Ladder gate: if an experiment record is provided,
        it MUST carry verdict == SUPPORTED. Untested or non-supported hypotheses are rejected.
        """
        if experiment_record is not None:
            if experiment_record.verdict != ExperimentVerdict.SUPPORTED:
                raise InvalidPromotionError(
                    f"Cannot promote hypothesis '{finding.hypothesis_id}' to Validated Finding: "
                    f"experiment verdict is '{experiment_record.verdict.value}', expected 'SUPPORTED'."
                )
            if experiment_record.experiment_id not in finding.supporting_experiment_ids:
                finding.supporting_experiment_ids.append(experiment_record.experiment_id)

        # Enforce Tier 4 demarcation
        finding.epistemic_tier = EpistemicTier.FINDING_VALIDATED
        finding.status = KnowledgeStatus.VALID
        now = datetime.now(timezone.utc).isoformat()
        if not finding.created_at:
            finding.created_at = now
        finding.updated_at = now

        self._findings[finding.finding_id] = finding

        # Register in audit log
        v_rec = FindingVersionRecord(
            record_id=f"ver-{uuid.uuid4().hex[:8]}",
            finding_id=finding.finding_id,
            version=finding.version,
            previous_status=None,
            new_status=KnowledgeStatus.VALID,
            change_type="CREATED",
            reason="Initial storage of experimentally supported validated finding.",
            timestamp=now,
        )
        if finding.finding_id not in self._audit_log:
            self._audit_log[finding.finding_id] = []
        self._audit_log[finding.finding_id].append(v_rec)

        # Update dependency graph
        for parent_id in finding.derived_from_finding_ids:
            if parent_id not in self._downstream_dependents:
                self._downstream_dependents[parent_id] = set()
            self._downstream_dependents[parent_id].add(finding.finding_id)

        return finding

    def invalidate_finding(
        self,
        finding_id: str,
        reason: str,
    ) -> Tuple[ValidatedFinding, DependentImpactReport]:
        """
        Formally invalidates a finding due to counterevidence, flawed assumptions, or retracting evidence.
        Updates finding status to INVALIDATED and triggers cascading dependent analysis.
        """
        finding = self.get_finding(finding_id)
        if not finding:
            raise FindingNotFoundError(f"Finding '{finding_id}' not found in knowledge memory.")

        old_status = finding.status
        finding.status = KnowledgeStatus.INVALIDATED
        finding.version += 1
        finding.invalidation_reason = reason
        now = datetime.now(timezone.utc).isoformat()
        finding.updated_at = now

        # Record version transition in audit trail
        v_rec = FindingVersionRecord(
            record_id=f"ver-{uuid.uuid4().hex[:8]}",
            finding_id=finding_id,
            version=finding.version,
            previous_status=old_status,
            new_status=KnowledgeStatus.INVALIDATED,
            change_type="INVALIDATED",
            reason=reason,
            timestamp=now,
        )
        self._audit_log[finding_id].append(v_rec)

        # Cascade analysis: identify all downstream findings requiring re-evaluation
        impact_report = self.get_affected_dependents(finding_id)
        return finding, impact_report

    def supersede_finding(
        self,
        old_finding_id: str,
        new_finding: ValidatedFinding,
        reason: str,
        new_experiment_record: Optional[ExperimentRecord] = None,
    ) -> Tuple[ValidatedFinding, ValidatedFinding, DependentImpactReport]:
        """
        Supersedes an outdated finding with a newer, higher-precision or broadened finding.
        Updates old finding to SUPERSEDED with superseded_by_id pointer, stores new finding,
        and computes dependent impact report.
        """
        old_finding = self.get_finding(old_finding_id)
        if not old_finding:
            raise FindingNotFoundError(f"Finding '{old_finding_id}' not found in knowledge memory.")

        # Store new finding first
        stored_new = self.store_validated_finding(new_finding, new_experiment_record)

        # Update old finding
        old_status = old_finding.status
        old_finding.status = KnowledgeStatus.SUPERSEDED
        old_finding.superseded_by_id = stored_new.finding_id
        old_finding.version += 1
        now = datetime.now(timezone.utc).isoformat()
        old_finding.updated_at = now

        v_rec = FindingVersionRecord(
            record_id=f"ver-{uuid.uuid4().hex[:8]}",
            finding_id=old_finding_id,
            version=old_finding.version,
            previous_status=old_status,
            new_status=KnowledgeStatus.SUPERSEDED,
            change_type="SUPERSEDED",
            reason=f"Superseded by finding '{stored_new.finding_id}': {reason}",
            timestamp=now,
        )
        self._audit_log[old_finding_id].append(v_rec)

        impact_report = self.get_affected_dependents(old_finding_id)
        return old_finding, stored_new, impact_report

    def get_finding(self, finding_id: str) -> Optional[ValidatedFinding]:
        """Retrieves a finding by ID."""
        return self._findings.get(finding_id)

    def list_findings(
        self,
        status_filter: Optional[KnowledgeStatus] = None,
        active_only: bool = True,
    ) -> List[ValidatedFinding]:
        """
        Lists findings in memory with optional status filtering.
        If active_only is True and no status_filter is given, defaults to status == VALID.
        """
        findings = list(self._findings.values())
        if status_filter:
            return [f for f in findings if f.status == status_filter]
        if active_only:
            return [f for f in findings if f.status == KnowledgeStatus.VALID]
        return findings

    def get_finding_history(self, finding_id: str) -> List[FindingVersionRecord]:
        """Returns the complete immutable version audit history for a finding."""
        if finding_id not in self._findings:
            raise FindingNotFoundError(f"Finding '{finding_id}' not found.")
        return list(self._audit_log.get(finding_id, []))

    def get_affected_dependents(self, finding_id: str) -> DependentImpactReport:
        """
        Executes breadth-first search (BFS) over the dependency graph to find all downstream
        findings directly and transitively derived from finding_id.
        """
        finding = self.get_finding(finding_id)
        status = finding.status if finding else KnowledgeStatus.INVALIDATED

        direct_children: List[str] = list(self._downstream_dependents.get(finding_id, set()))
        transitive_children: Set[str] = set()

        queue = deque(direct_children)
        visited = set(direct_children)

        while queue:
            curr = queue.popleft()
            downstream = self._downstream_dependents.get(curr, set())
            for nxt in downstream:
                if nxt not in visited and nxt != finding_id:
                    visited.add(nxt)
                    transitive_children.add(nxt)
                    queue.append(nxt)

        all_affected = list(direct_children) + list(transitive_children)
        return DependentImpactReport(
            trigger_finding_id=finding_id,
            trigger_status=status,
            directly_affected_finding_ids=direct_children,
            transitively_affected_finding_ids=list(transitive_children),
            total_affected_count=len(all_affected),
        )

    def check_finding_integrity(self, finding_id: str) -> Tuple[bool, List[str]]:
        """
        Checks whether a finding's dependencies remain sound.
        Returns (is_sound, issues_list).
        If any upstream dependency is INVALIDATED or SUPERSEDED, the finding's integrity is compromised.
        """
        finding = self.get_finding(finding_id)
        if not finding:
            raise FindingNotFoundError(f"Finding '{finding_id}' not found.")

        issues: List[str] = []
        is_sound = True

        for parent_id in finding.derived_from_finding_ids:
            parent = self.get_finding(parent_id)
            if not parent:
                issues.append(f"Prerequisite finding '{parent_id}' does not exist in memory.")
                is_sound = False
            elif parent.status == KnowledgeStatus.INVALIDATED:
                issues.append(f"Prerequisite finding '{parent_id}' has been INVALIDATED ({parent.invalidation_reason}).")
                is_sound = False
            elif parent.status == KnowledgeStatus.SUPERSEDED:
                issues.append(f"Prerequisite finding '{parent_id}' has been SUPERSEDED by '{parent.superseded_by_id}'.")
                is_sound = False

        return is_sound, issues
