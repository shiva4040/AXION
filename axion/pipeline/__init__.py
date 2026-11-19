"""
AXION Cognitive Pipeline Package (Phase 1).
Contains the formal Eight-Stage Cognitive Architecture implementations,
pipeline coordinator, and stage data models.
"""

from axion.pipeline.types import (
    AcquiredChunk,
    AcquisitionPayload,
    ComposedSystem,
    ExtractedClaim,
    PipelineAnswerResponse,
    QuestionIntent,
    QuestionSpec,
    ReasoningTrace,
    StageExecutionLog,
    SupportingEvidenceItem,
    VerificationAuditReport,
)
from axion.pipeline.stage01_question import MinimalQuestionProcessor
from axion.pipeline.stage02_acquisition import KnowledgeAcquisitionCoordinator
from axion.pipeline.coordinator import PipelineCoordinator

__all__ = [
    "AcquiredChunk",
    "AcquisitionPayload",
    "ComposedSystem",
    "ExtractedClaim",
    "PipelineAnswerResponse",
    "QuestionIntent",
    "QuestionSpec",
    "ReasoningTrace",
    "StageExecutionLog",
    "SupportingEvidenceItem",
    "VerificationAuditReport",
    "MinimalQuestionProcessor",
    "KnowledgeAcquisitionCoordinator",
    "PipelineCoordinator",
]
