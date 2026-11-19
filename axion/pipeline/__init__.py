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
    VerificationVerdict,
)
from axion.pipeline.stage01_question import MinimalQuestionProcessor
from axion.pipeline.stage02_acquisition import KnowledgeAcquisitionCoordinator
from axion.pipeline.stage03_extraction import MinimalEvidenceExtractor
from axion.pipeline.stage04_composition import MinimalKnowledgeComposer
from axion.pipeline.stage05_reasoning import MinimalReasoner
from axion.pipeline.stage06_verification import IndependentVerificationGuard
from axion.pipeline.stage07_memory import VerifiedMemoryManager
from axion.pipeline.stage08_answer import MinimalAnswerGenerator
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
    "VerificationVerdict",
    "MinimalQuestionProcessor",
    "KnowledgeAcquisitionCoordinator",
    "MinimalEvidenceExtractor",
    "MinimalKnowledgeComposer",
    "MinimalReasoner",
    "IndependentVerificationGuard",
    "VerifiedMemoryManager",
    "MinimalAnswerGenerator",
    "PipelineCoordinator",
]
