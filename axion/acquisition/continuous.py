import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from axion.acquisition.types import (
    ContinuousSourceConfig, SearchRequest, SearchResponse, SourceDocument, AcquisitionMode
)
from axion.acquisition.engine import InformationAcquisitionEngine

logger = logging.getLogger(__name__)

DEFAULT_STATE_FILE = "axion_continuous_acquisition_state.json"

class ContinuousAcquisitionManager:
    """
    Manages standing, scheduled, and continuous discovery feeds.
    Tracks update frequencies, prevents re-processing known publications,
    and supports automated knowledge stream polling.
    """

    def __init__(self, persistence_file: str = DEFAULT_STATE_FILE):
        self.persistence_file = Path(persistence_file)
        self.configs: Dict[str, ContinuousSourceConfig] = {}
        self._load_state()

    def add_subscription(
        self,
        source_name: str,
        search_query: str,
        poll_interval_seconds: int = 3600,
        enabled: bool = True
    ) -> ContinuousSourceConfig:
        """Registers a continuous topic subscription for automated external polling."""
        cfg = ContinuousSourceConfig(
            source_name=source_name,
            search_query=search_query,
            poll_interval_seconds=poll_interval_seconds,
            enabled=enabled,
            last_poll_timestamp=None,
            seen_identifiers=[]
        )
        self.configs[cfg.config_id] = cfg
        self._save_state()
        return cfg

    def list_subscriptions(self) -> List[ContinuousSourceConfig]:
        """Lists all active and configured continuous discovery topics."""
        return list(self.configs.values())

    def remove_subscription(self, config_id: str) -> bool:
        """Removes a subscription by ID."""
        if config_id in self.configs:
            del self.configs[config_id]
            self._save_state()
            return True
        return False

    async def poll_subscription(
        self,
        config_id: str,
        engine: InformationAcquisitionEngine,
        session: Optional[AsyncSession] = None,
        auto_ingest: bool = False
    ) -> Dict[str, Any]:
        """
        Polls a specific topic subscription.
        Deduplicates against previously seen identifiers and optionally ingests new records.
        """
        cfg = self.configs.get(config_id)
        if not cfg or not cfg.enabled:
            return {"status": "skipped", "reason": "Config disabled or not found"}

        now_iso = datetime.now(timezone.utc).isoformat()
        search_req = SearchRequest(
            query=cfg.search_query,
            sources=[cfg.source_name] if cfg.source_name != "all" else None,
            max_results_per_source=10,
            mode=AcquisitionMode.CONTINUOUS
        )

        search_resp: SearchResponse = await engine.search(search_req)

        # Filter out previously seen identifiers
        seen_set = set(cfg.seen_identifiers)
        new_docs: List[SourceDocument] = []
        for doc in search_resp.documents:
            identifier = doc.doi or doc.source_url or doc.title.lower().strip()
            if identifier not in seen_set:
                new_docs.append(doc)
                seen_set.add(identifier)

        cfg.seen_identifiers = list(seen_set)
        cfg.last_poll_timestamp = now_iso
        self._save_state()

        ingested_summary = None
        if auto_ingest and new_docs and session:
            ingested_summary = await engine.ingest_documents(new_docs, session=session)

        return {
            "config_id": config_id,
            "query": cfg.search_query,
            "source": cfg.source_name,
            "total_discovered": search_resp.total_discovered,
            "new_documents_count": len(new_docs),
            "new_documents": [d.model_dump() for d in new_docs],
            "ingested_summary": ingested_summary.model_dump() if ingested_summary else None,
            "polled_at": now_iso
        }

    async def poll_all_subscriptions(
        self,
        engine: InformationAcquisitionEngine,
        session: Optional[AsyncSession] = None,
        auto_ingest: bool = False
    ) -> List[Dict[str, Any]]:
        """Polls all enabled subscriptions concurrently."""
        results = []
        for cfg_id in list(self.configs.keys()):
            res = await self.poll_subscription(cfg_id, engine, session=session, auto_ingest=auto_ingest)
            results.append(res)
        return results

    def _load_state(self):
        """Loads subscription configs from disk."""
        if not self.persistence_file.exists():
            return
        try:
            with open(self.persistence_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data.get("subscriptions", []):
                    cfg = ContinuousSourceConfig(**item)
                    self.configs[cfg.config_id] = cfg
        except Exception as e:
            logger.warning("Could not load continuous acquisition state: %s", e)

    def _save_state(self):
        """Saves subscription configs to disk."""
        try:
            data = {
                "subscriptions": [cfg.model_dump() for cfg in self.configs.values()],
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            with open(self.persistence_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning("Could not save continuous acquisition state: %s", e)
