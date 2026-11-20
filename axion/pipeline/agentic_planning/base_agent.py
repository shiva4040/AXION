"""Base class for all specialized research planning agents in AXION Stage 01."""

import json
import logging
import re
import uuid
import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from axion.core.provider import ChatMessage, LLMProvider, MockProvider
from axion.pipeline.agentic_planning.types import (
    AgentFinding,
    AgentRole,
    AgentStatus,
    AgentStatusRecord,
    AgenticResearchState,
    FindingType,
    TimelineEvent,
)

logger = logging.getLogger(__name__)


class BaseResearchAgent:
    """
    Base class for all specialized research planning agents in AXION Stage 01.
    Equipped with LLM prompting capability (Google Gemini), robust JSON extraction,
    deterministic scientific fallback models, structured finding recording, and execution telemetry.
    """

    def __init__(
        self,
        role: AgentRole,
        display_name: str = "",
        name: str = "",
        responsibility: str = "",
        provider: Optional[LLMProvider] = None,
        llm_provider: Optional[LLMProvider] = None,
    ):
        self.role = role
        self.display_name = display_name or name or (role.value if hasattr(role, "value") else str(role))
        self.name = self.display_name
        self.responsibility = responsibility or self.display_name
        self.provider = provider or llm_provider

    def _extract_json_payload(self, text: str) -> Optional[Dict[str, Any]]:
        """Extracts JSON payload from text, stripping markdown code fences."""
        clean = text.strip()
        try:
            return json.loads(clean)
        except Exception:
            pass

        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", clean)
        if fence_match:
            try:
                return json.loads(fence_match.group(1).strip())
            except Exception:
                pass

        start = clean.find("{")
        end = clean.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(clean[start:end + 1])
            except Exception:
                pass
        return None

    def call_llm_json(
        self,
        prompt: str,
        state: Optional[AgenticResearchState] = None,
        max_tokens: int = 1500,
        temperature: float = 0.0,
    ) -> Optional[Dict[str, Any]]:
        """Synchronously invokes LLM provider if configured and returns parsed JSON object."""
        if not self.provider or isinstance(self.provider, MockProvider):
            return None

        try:
            messages = [
                ChatMessage(
                    role="system",
                    content=f"You are the AXION {self.display_name}. Return strictly valid JSON conforming to the requested schema.",
                ),
                ChatMessage(role="user", content=prompt),
            ]

            # Run in asyncio loop or new loop if synchronous
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as pool:
                        resp = pool.submit(
                            asyncio.run,
                            self.provider.generate_text(
                                messages=messages,
                                temperature=temperature,
                                max_tokens=max_tokens,
                            )
                        ).result(timeout=25)
                else:
                    resp = loop.run_until_complete(
                        self.provider.generate_text(
                            messages=messages,
                            temperature=temperature,
                            max_tokens=max_tokens,
                        )
                    )
            except Exception as loop_err:
                logger.warning(f"Async loop invocation fallback: {loop_err}")
                return None

            return self._extract_json_payload(resp.text)
        except Exception as e:
            logger.warning(f"Agent {self.display_name} LLM call error: {e}")
            return None

    async def _call_llm_json(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1500,
        temperature: float = 0.0,
    ) -> Optional[Dict[str, Any]]:
        """Asynchronous LLM invocation for async agent investigate() methods."""
        if not self.provider or isinstance(self.provider, MockProvider):
            return None
        try:
            messages = [
                ChatMessage(role="system", content=system_prompt),
                ChatMessage(role="user", content=user_prompt),
            ]
            resp = await self.provider.generate_text(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return self._extract_json_payload(resp.text)
        except Exception as e:
            logger.warning(f"Agent {self.display_name} LLM call error: {e}")
            return None

    def set_active(self, state: AgenticResearchState, task_desc: Optional[str] = None) -> None:
        """Marks this agent as actively investigating in the shared state."""
        role_key = self.role.value if hasattr(self.role, "value") else str(self.role)
        rec = state.agent_statuses.get(role_key) or state.agents.get(role_key)
        if not rec:
            rec = AgentStatusRecord(
                agent_id=f"ag-{role_key[:8]}",
                role=self.role,
                display_name=self.display_name,
                name=self.display_name,
                responsibility=self.responsibility,
                status=AgentStatus.INVESTIGATING,
                current_task=task_desc or f"Investigating {self.display_name}",
            )
            state.agent_statuses[role_key] = rec
            state.agents[role_key] = rec
        else:
            rec.status = AgentStatus.INVESTIGATING
            rec.current_task = task_desc or f"Investigating {self.display_name}"

    def set_completed(self, state: AgenticResearchState, findings_count: int = 1) -> None:
        """Marks this agent as completed in the shared state."""
        role_key = self.role.value if hasattr(self.role, "value") else str(self.role)
        rec = state.agent_statuses.get(role_key) or state.agents.get(role_key)
        if rec:
            rec.status = AgentStatus.COMPLETED
            rec.findings_count = max(rec.findings_count, findings_count)
            state.agent_statuses[role_key] = rec
            state.agents[role_key] = rec
        else:
            rec = AgentStatusRecord(
                agent_id=f"ag-{role_key[:8]}",
                role=self.role,
                display_name=self.display_name,
                name=self.display_name,
                responsibility=self.responsibility,
                status=AgentStatus.COMPLETED,
                findings_count=findings_count,
            )
            state.agent_statuses[role_key] = rec
            state.agents[role_key] = rec

        self.log_timeline(
            state,
            action="COMPLETED",
            summary=f"{self.display_name} concluded analysis with {findings_count} findings",
            round_number=state.current_round,
        )

    def record_finding(
        self,
        state: AgenticResearchState,
        finding_type: FindingType,
        title: str,
        content: str,
        scientific_basis: str = "",
        justification: str = "",
        subquestions: Optional[List[str]] = None,
        domains: Optional[List[str]] = None,
        confidence: float = 0.90,
        equations: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
    ) -> AgentFinding:
        """Helper to create and append an atomic AgentFinding to shared research state."""
        effective_justification = scientific_basis or justification or "Standard physical laws and verified models."
        finding = AgentFinding(
            agent_role=self.role,
            finding_type=finding_type,
            title=title,
            content=content,
            scientific_justification=effective_justification,
            related_subquestions=subquestions or [],
            related_domains=domains or [],
            confidence=confidence,
        )
        if finding not in state.all_findings:
            state.all_findings.append(finding)
        if finding not in state.findings:
            state.findings.append(finding)
        return finding

    def log_timeline(
        self,
        state: AgenticResearchState,
        action: str = "",
        summary: str = "",
        event_type: str = "",
        description: str = "",
        status: str = "SUCCESS",
        round_number: int = 1,
    ) -> None:
        """Appends a timestamped chronological event to the investigation timeline."""
        effective_action = action or event_type or "AGENT_STEP"
        effective_summary = summary or description or f"{self.display_name} executed research step"
        state.timeline.append(
            TimelineEvent(
                stage=f"Round {round_number}",
                agent_role=self.display_name,
                action=effective_action,
                status=status,
                summary=effective_summary,
            )
        )

    def execute(self, state: AgenticResearchState, context: Optional[Dict[str, Any]] = None) -> AgenticResearchState:
        """Synchronously executes the agent's research logic and updates state."""
        # If subclass overrides investigate but not execute, invoke investigate
        if type(self).investigate != BaseResearchAgent.investigate:
            try:
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                if loop.is_running():
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as pool:
                        status_rec = pool.submit(asyncio.run, self.investigate(state)).result(timeout=30)
                else:
                    status_rec = loop.run_until_complete(self.investigate(state))

                # Ensure status is reflected in both agent_statuses and agents
                role_key = self.role.value if hasattr(self.role, "value") else str(self.role)
                if status_rec:
                    state.agent_statuses[role_key] = status_rec
                    state.agents[role_key] = status_rec
            except Exception as e:
                logger.warning(f"Agent {self.display_name} synchronous execute fallback: {e}")
        return state

    async def investigate(self, state: AgenticResearchState) -> AgentStatusRecord:
        """Asynchronously executes specialized investigation and returns status record."""
        self.execute(state)
        role_key = self.role.value if hasattr(self.role, "value") else str(self.role)
        return state.agent_statuses.get(role_key) or AgentStatusRecord(
            agent_id=f"ag-{role_key[:8]}",
            role=self.role,
            display_name=self.display_name,
            responsibility=self.responsibility,
            status=AgentStatus.COMPLETED,
        )
