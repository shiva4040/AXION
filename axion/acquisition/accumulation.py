import re
import uuid
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from axion.acquisition.types import SourceDocument, DocumentType, AccessStatus
from axion.database.models import (
    AccumulatedKnowledgeRecord, CrossDomainConnectionRecord, Document, DocumentChunk
)

logger = logging.getLogger(__name__)

# Common scientific equation patterns
EQUATION_PATTERNS = [
    r"\b([A-Za-z_][A-Za-z0-9_\^\\]*)\s*=\s*([^,\n\;]+?)(?=[,\;\n]|\.\s|$)",
    r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\((?:t|x|v|r)\)\s*=\s*([^,\n\;]+?)(?=[,\;\n]|\.\s|$)",
]

# Physical variable indicator regexes
VARIABLE_MAP = {
    "P": "Power",
    "I": "Electric Current",
    "R": "Electrical Resistance",
    "V": "Voltage / Potential",
    "v": "Velocity",
    "F": "Force",
    "F_drag": "Aerodynamic Drag Force",
    "rho": "Fluid Density",
    "C_d": "Drag Coefficient",
    "A": "Area / Surface Area",
    "G": "Solar Irradiance / Radiation",
    "eta": "Efficiency",
    "T": "Temperature",
    "m": "Mass",
    "a": "Acceleration",
    "E": "Energy",
    "c": "Speed of Light",
    "h": "Planck Constant",
    "k": "Boltzmann Constant",
}

# Domain keywords for classification
DOMAIN_KEYWORDS = {
    "aerodynamics": ["aerodynamic", "drag", "lift", "airflow", "reynolds", "wing", "fluid", "wake", "boundary layer"],
    "photovoltaics": ["photovoltaic", "solar", "pv", "irradiance", "cell efficiency", "silicon", "insolation"],
    "electromagnetism": ["circuit", "current", "resistance", "voltage", "capacitance", "inductance", "magnetic", "ohm"],
    "thermodynamics": ["thermal", "heat", "entropy", "temperature", "enthalpy", "carnot", "convection"],
    "high_energy_physics": ["boson", "higgs", "hadron", "quark", "lepton", "neutrino", "qft", "cern", "parton"],
    "astrophysics": ["galaxy", "stellar", "black hole", "cosmology", "redshift", "supernova", "astronomical"],
    "quantum_mechanics": ["wavefunction", "schrodinger", "hamiltonian", "quantum", "spin", "eigenstate"]
}

class KnowledgeAccumulator:
    """
    Component: Scientific Knowledge Accumulation Subsystem.
    Processes acquired scientific papers and excerpts into persistent, structured
    scientific knowledge: claims, equations, entities, parameters, assumptions,
    boundary conditions, and cross-domain relational bridges.
    Directly feeds Stages 03-08.
    """

    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session
        self._in_memory_items: List[AccumulatedKnowledgeRecord] = []
        self._in_memory_connections: List[CrossDomainConnectionRecord] = []
        self._seen_content_hashes: Set[str] = set()

    def infer_domain(self, text: str, default: str = "general_science") -> str:
        """Determines scientific domain based on lexical occurrence frequency."""
        t_lower = text.lower()
        counts = {
            domain: sum(1 for kw in kws if kw in t_lower)
            for domain, kws in DOMAIN_KEYWORDS.items()
        }
        best_domain, max_count = max(counts.items(), key=lambda x: x[1])
        return best_domain if max_count > 0 else default

    def extract_equations_and_variables(self, text: str) -> List[Dict[str, Any]]:
        """Extracts mathematical formulas, symbols, and declared variables."""
        extracted: List[Dict[str, Any]] = []
        seen_eq = set()

        for pat in EQUATION_PATTERNS:
            for match in re.finditer(pat, text):
                lhs, rhs = match.groups()
                lhs_c = lhs.strip()
                rhs_c = rhs.strip().rstrip(".")
                eq_str = f"{lhs_c} = {rhs_c}"

                if len(lhs_c) <= 25 and len(rhs_c) >= 2 and eq_str not in seen_eq:
                    seen_eq.add(eq_str)
                    # Extract variables mentioned in formula
                    tokens = set(re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", eq_str))
                    var_dict = {
                        token: VARIABLE_MAP.get(token, f"Physical parameter {token}")
                        for token in tokens if len(token) <= 8 and token not in {"the", "and", "for", "with", "from"}
                    }
                    extracted.append({
                        "equation": eq_str,
                        "lhs": lhs_c,
                        "rhs": rhs_c,
                        "variables": var_dict
                    })
        return extracted

    def extract_assumptions_and_limits(self, text: str) -> Tuple[List[str], List[str]]:
        """Extracts scientific assumptions and physical boundary conditions."""
        assumptions: List[str] = []
        boundary_conditions: List[str] = []

        # Assumption indicators
        assumption_patterns = [
            r"assuming\s+([^,\.\;\n]+)",
            r"under\s+(?:the\s+)?condition\s+(?:that\s+)?([^,\.\;\n]+)",
            r"in\s+the\s+limit\s+of\s+([^,\.\;\n]+)",
            r"treated\s+as\s+([^,\.\;\n]+)",
            r"(steady[- ]state\s+conditions?)",
            r"(incompressible\s+flow)",
            r"(laminar\s+flow)",
            r"(ideal\s+gas\s+approximation)"
        ]
        for pat in assumption_patterns:
            for match in re.finditer(pat, text, re.IGNORECASE):
                val = match.group(1).strip()
                if len(val) > 3 and val.lower() not in [a.lower() for a in assumptions]:
                    assumptions.append(val)

        # Boundary condition indicators
        bc_patterns = [
            r"([A-Za-z0-9_\\]+\s*(?:<|>|<=|>=|=)\s*[^,\.\;\n]+)",
            r"(boundary\s+condition[^,\.\;\n]+)",
            r"(reynolds\s+number\s+Re\s*<\s*\d+)",
            r"(temperature\s+range\s+[^,\.\;\n]+)",
        ]
        for pat in bc_patterns:
            for match in re.finditer(pat, text, re.IGNORECASE):
                val = match.group(1).strip()
                if len(val) > 3 and val.lower() not in [b.lower() for b in boundary_conditions]:
                    boundary_conditions.append(val)

        return assumptions, boundary_conditions

    def extract_claims(self, text: str) -> List[str]:
        """Extracts substantive empirical and theoretical scientific claims."""
        claims: List[str] = []
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 20]

        claim_cues = [
            "increases with", "decreases with", "scales quadratically", "scales linearly",
            "is proportional to", "counteracts", "enhances", "governs", "demonstrates",
            "we find that", "results indicate", "dissipates", "counterbalanced by", "exceeds"
        ]

        for s in sentences:
            s_clean = s.strip()
            if any(cue in s_clean.lower() for cue in claim_cues):
                if s_clean not in claims:
                    claims.append(s_clean)

        return claims

    def detect_contradiction(
        self,
        new_item: AccumulatedKnowledgeRecord,
        existing_items: List[AccumulatedKnowledgeRecord]
    ) -> Optional[Tuple[AccumulatedKnowledgeRecord, str]]:
        """
        Detects opposing claims or incompatible parameter behaviors.
        Example: Item A asserts "power increases with velocity", Item B asserts "power decreases with velocity".
        """
        for ex in existing_items:
            if ex.domain == new_item.domain and ex.item_type == new_item.item_type:
                new_t = new_item.content.lower()
                ex_t = ex.content.lower()

                # Contradiction pattern: increases vs decreases for identical concept
                if ("increases with" in new_t and "decreases with" in ex_t) or \
                   ("decreases with" in new_t and "increases with" in ex_t):
                    new_vars = new_item.variables or {}
                    ex_vars = ex.variables or {}
                    shared_vars = set(new_vars.keys()).intersection(set(ex_vars.keys()))
                    if shared_vars or any(k in ex_t for k in new_vars.keys()):
                        reason = f"Directional contradiction on relationship: '{new_item.content[:80]}' vs '{ex.content[:80]}'"
                        return ex, reason
        return None

    def identify_cross_domain_connections(
        self,
        new_item: AccumulatedKnowledgeRecord,
        existing_items: List[AccumulatedKnowledgeRecord]
    ) -> List[CrossDomainConnectionRecord]:
        """
        Discovers bridge relationships linking concepts across disparate scientific disciplines.
        Example: Aerodynamic drag energy loss in fluid dynamics <-> Photovoltaic power output in solar energy.
        """
        connections: List[CrossDomainConnectionRecord] = []
        if not new_item.domain:
            return connections

        new_vars = new_item.variables or {}
        new_text = f"{new_item.source_title} {new_item.content}".lower()
        for ex in existing_items:
            if ex.domain != new_item.domain and ex.id != new_item.id:
                ex_vars = ex.variables or {}
                ex_text = f"{ex.source_title} {ex.content}".lower()
                # Check for shared foundational physics quantities (Power, Energy, Velocity, Area, Temperature)
                shared_quantities = set(k.lower() for k in new_vars.keys()).intersection(set(k.lower() for k in ex_vars.keys()))

                # Check for analogical / coupling terms
                coupling_term = None
                p_terms = {"power", "energy", "work", "propulsion", "transfer", "efficiency", "dissipation"}
                new_matches = set(new_text.split()).intersection(p_terms)
                ex_matches = set(ex_text.split()).intersection(p_terms)

                if new_matches and ex_matches:
                    shared_keywords = new_matches.intersection(ex_matches) or new_matches
                    coupling_term = f"Energy/Power Transfer ({', '.join(sorted(shared_keywords))})"
                elif shared_quantities:
                    coupling_term = f"Shared Parameter: {', '.join(sorted(shared_quantities))}"

                if coupling_term:
                    conn = CrossDomainConnectionRecord(
                        id=f"bridge-{uuid.uuid4().hex[:12]}",
                        source_item_id=ex.id,
                        target_item_id=new_item.id,
                        source_domain=ex.domain,
                        target_domain=new_item.domain,
                        bridge_type="analogical_transfer" if "power" in coupling_term.lower() else "shared_parameter",
                        shared_concept=coupling_term,
                        confidence=0.88,
                        description=(
                            f"Cross-domain bridge connecting [{ex.domain}] '{ex.source_title}' "
                            f"with [{new_item.domain}] '{new_item.source_title}' via {coupling_term}."
                        )
                    )
                    connections.append(conn)

        return connections

    async def accumulate_document(
        self,
        doc: SourceDocument,
        session: Optional[AsyncSession] = None
    ) -> List[AccumulatedKnowledgeRecord]:
        """
        Core ingestion pipeline: Extracts equations, claims, assumptions, boundary conditions,
        and constructs cross-domain relational bridges from an acquired document.
        """
        db = session or self.session
        text = doc.content
        domain = self.infer_domain(text + " " + doc.title, default="general_science")
        provenance = {
            "source_name": doc.source_name,
            "source_url": doc.source_url,
            "doi": doc.doi,
            "retrieval_date": doc.retrieval_date,
            "document_id": doc.id,
            "authors": doc.authors,
            "publication_date": doc.publication_date
        }

        created_items: List[AccumulatedKnowledgeRecord] = []

        # 1. Extract Equations
        eqs = self.extract_equations_and_variables(text)
        for eq_data in eqs:
            content_hash = f"eq:{eq_data['equation']}"
            if content_hash in self._seen_content_hashes:
                continue
            self._seen_content_hashes.add(content_hash)

            item = AccumulatedKnowledgeRecord(
                id=f"accum-{uuid.uuid4().hex[:12]}",
                document_id=doc.id,
                source_name=doc.source_name,
                source_title=doc.title,
                doi=doc.doi,
                domain=domain,
                item_type="equation",
                content=eq_data["equation"],
                canonical_symbol=eq_data["lhs"],
                variables=eq_data["variables"],
                confidence=0.98,
                provenance=provenance
            )
            created_items.append(item)

        # 2. Extract Claims
        claims = self.extract_claims(text)
        for cl in claims:
            content_hash = f"cl:{cl.strip()}"
            if content_hash in self._seen_content_hashes:
                continue
            self._seen_content_hashes.add(content_hash)

            # Check variables in claim
            vars_found = {
                k: v for k, v in VARIABLE_MAP.items()
                if f" {k} " in f" {cl} " or v.lower() in cl.lower()
            }

            item = AccumulatedKnowledgeRecord(
                id=f"accum-{uuid.uuid4().hex[:12]}",
                document_id=doc.id,
                source_name=doc.source_name,
                source_title=doc.title,
                doi=doc.doi,
                domain=domain,
                item_type="claim",
                content=cl,
                variables=vars_found,
                confidence=0.92,
                provenance=provenance
            )
            # Contradiction detection against prior accumulated items
            all_known = list(self._in_memory_items) + created_items
            contra = self.detect_contradiction(item, all_known)
            if contra:
                conflicting_item, reason = contra
                item.is_contradicted = True
                item.contradiction_notes = reason
                conflicting_item.is_contradicted = True
                conflicting_item.contradiction_notes = reason

            created_items.append(item)

        # 3. Extract Assumptions & Boundary Conditions
        assumptions, bcs = self.extract_assumptions_and_limits(text)
        for asm in assumptions:
            content_hash = f"asm:{asm.strip()}"
            if content_hash in self._seen_content_hashes:
                continue
            self._seen_content_hashes.add(content_hash)

            item = AccumulatedKnowledgeRecord(
                id=f"accum-{uuid.uuid4().hex[:12]}",
                document_id=doc.id,
                source_name=doc.source_name,
                source_title=doc.title,
                doi=doc.doi,
                domain=domain,
                item_type="assumption",
                content=asm,
                assumptions=[asm],
                confidence=0.90,
                provenance=provenance
            )
            created_items.append(item)

        for bc in bcs:
            content_hash = f"bc:{bc.strip()}"
            if content_hash in self._seen_content_hashes:
                continue
            self._seen_content_hashes.add(content_hash)

            item = AccumulatedKnowledgeRecord(
                id=f"accum-{uuid.uuid4().hex[:12]}",
                document_id=doc.id,
                source_name=doc.source_name,
                source_title=doc.title,
                doi=doc.doi,
                domain=domain,
                item_type="boundary_condition",
                content=bc,
                boundary_conditions=[bc],
                confidence=0.90,
                provenance=provenance
            )
            created_items.append(item)

        # Cross-Domain Bridge Formation
        new_bridges: List[CrossDomainConnectionRecord] = []
        all_accumulated = list(self._in_memory_items)
        for it in created_items:
            bridges = self.identify_cross_domain_connections(it, all_accumulated)
            new_bridges.extend(bridges)

        # Update In-Memory cache
        self._in_memory_items.extend(created_items)
        self._in_memory_connections.extend(new_bridges)

        # Persist to DB if session is active
        if db:
            for it in created_items:
                db.add(it)
            for br in new_bridges:
                db.add(br)
            await db.commit()

        return created_items

    async def get_statistics(self, session: Optional[AsyncSession] = None) -> Dict[str, Any]:
        """
        Dynamically calculates actual acquisition and accumulation metrics.
        Guaranteed: No mock or placeholder numbers.
        """
        db = session or self.session

        if db:
            try:
                # Count DB documents
                d_stmt = select(func.count(Document.id))
                doc_count = (await db.execute(d_stmt)).scalar() or 0

                # Count accumulated items by type
                i_stmt = select(AccumulatedKnowledgeRecord.item_type, func.count(AccumulatedKnowledgeRecord.id)).group_by(AccumulatedKnowledgeRecord.item_type)
                i_res = (await db.execute(i_stmt)).all()
                type_counts = {row[0]: row[1] for row in i_res}

                # Count domain distribution
                dom_stmt = select(AccumulatedKnowledgeRecord.domain, func.count(AccumulatedKnowledgeRecord.id)).group_by(AccumulatedKnowledgeRecord.domain)
                dom_res = (await db.execute(dom_stmt)).all()
                dom_counts = {row[0]: row[1] for row in dom_res}

                # Count source distribution
                src_stmt = select(AccumulatedKnowledgeRecord.source_name, func.count(AccumulatedKnowledgeRecord.id)).group_by(AccumulatedKnowledgeRecord.source_name)
                src_res = (await db.execute(src_stmt)).all()
                src_counts = {row[0]: row[1] for row in src_res}

                # Count cross-domain bridges
                br_stmt = select(func.count(CrossDomainConnectionRecord.id))
                bridge_count = (await db.execute(br_stmt)).scalar() or 0

                # Count contradictions
                contra_stmt = select(func.count(AccumulatedKnowledgeRecord.id)).where(AccumulatedKnowledgeRecord.is_contradicted == True)
                contra_count = (await db.execute(contra_stmt)).scalar() or 0

                return {
                    "total_documents_retrieved": doc_count,
                    "total_claims": type_counts.get("claim", 0),
                    "total_equations": type_counts.get("equation", 0),
                    "total_assumptions": type_counts.get("assumption", 0),
                    "total_boundary_conditions": type_counts.get("boundary_condition", 0),
                    "total_knowledge_items": sum(type_counts.values()),
                    "total_cross_domain_connections": bridge_count,
                    "total_contradictions_detected": contra_count,
                    "domain_distribution": dom_counts,
                    "source_distribution": src_counts
                }
            except Exception as e:
                logger.warning("DB query for accumulation stats failed: %s; using memory cache", e)

        # In-memory fallback
        type_counts = {}
        dom_counts = {}
        src_counts = {}
        for it in self._in_memory_items:
            type_counts[it.item_type] = type_counts.get(it.item_type, 0) + 1
            dom_counts[it.domain] = dom_counts.get(it.domain, 0) + 1
            src_counts[it.source_name] = src_counts.get(it.source_name, 0) + 1

        return {
            "total_documents_retrieved": len(set(it.document_id for it in self._in_memory_items if it.document_id)),
            "total_claims": type_counts.get("claim", 0),
            "total_equations": type_counts.get("equation", 0),
            "total_assumptions": type_counts.get("assumption", 0),
            "total_boundary_conditions": type_counts.get("boundary_condition", 0),
            "total_knowledge_items": len(self._in_memory_items),
            "total_cross_domain_connections": len(self._in_memory_connections),
            "total_contradictions_detected": sum(1 for it in self._in_memory_items if it.is_contradicted),
            "domain_distribution": dom_counts,
            "source_distribution": src_counts
        }

    async def get_items(
        self,
        domain: Optional[str] = None,
        item_type: Optional[str] = None,
        session: Optional[AsyncSession] = None
    ) -> List[Dict[str, Any]]:
        """Returns structured accumulated knowledge records."""
        db = session or self.session
        if db:
            try:
                stmt = select(AccumulatedKnowledgeRecord)
                if domain:
                    stmt = stmt.where(AccumulatedKnowledgeRecord.domain == domain)
                if item_type:
                    stmt = stmt.where(AccumulatedKnowledgeRecord.item_type == item_type)
                stmt = stmt.order_by(AccumulatedKnowledgeRecord.created_at.desc())
                res = await db.execute(stmt)
                rows = res.scalars().all()
                return [
                    {
                        "id": r.id,
                        "document_id": r.document_id,
                        "source_name": r.source_name,
                        "source_title": r.source_title,
                        "doi": r.doi,
                        "domain": r.domain,
                        "item_type": r.item_type,
                        "content": r.content,
                        "canonical_symbol": r.canonical_symbol,
                        "variables": r.variables or {},
                        "assumptions": r.assumptions or [],
                        "boundary_conditions": r.boundary_conditions or [],
                        "confidence": r.confidence,
                        "is_contradicted": r.is_contradicted,
                        "contradiction_notes": r.contradiction_notes,
                        "provenance": r.provenance or {},
                        "created_at": r.created_at.isoformat() if r.created_at else None
                    }
                    for r in rows
                ]
            except Exception as e:
                logger.warning("DB query for accumulated items failed: %s", e)

        # In-memory fallback
        items = self._in_memory_items
        if domain:
            items = [i for i in items if i.domain == domain]
        if item_type:
            items = [i for i in items if i.item_type == item_type]

        return [
            {
                "id": r.id,
                "document_id": r.document_id,
                "source_name": r.source_name,
                "source_title": r.source_title,
                "doi": r.doi,
                "domain": r.domain,
                "item_type": r.item_type,
                "content": r.content,
                "canonical_symbol": r.canonical_symbol,
                "variables": r.variables or {},
                "assumptions": r.assumptions or [],
                "boundary_conditions": r.boundary_conditions or [],
                "confidence": r.confidence,
                "is_contradicted": r.is_contradicted,
                "contradiction_notes": r.contradiction_notes,
                "provenance": r.provenance or {},
                "created_at": r.created_at.isoformat() if hasattr(r, "created_at") and r.created_at else None
            }
            for r in items
        ]

    async def get_connections(
        self,
        session: Optional[AsyncSession] = None
    ) -> List[Dict[str, Any]]:
        """Returns cross-domain connection bridges."""
        db = session or self.session
        if db:
            try:
                stmt = select(CrossDomainConnectionRecord).order_by(CrossDomainConnectionRecord.created_at.desc())
                res = await db.execute(stmt)
                rows = res.scalars().all()
                return [
                    {
                        "id": r.id,
                        "source_item_id": r.source_item_id,
                        "target_item_id": r.target_item_id,
                        "source_domain": r.source_domain,
                        "target_domain": r.target_domain,
                        "bridge_type": r.bridge_type,
                        "shared_concept": r.shared_concept,
                        "confidence": r.confidence,
                        "description": r.description
                    }
                    for r in rows
                ]
            except Exception as e:
                logger.warning("DB query for cross-domain bridges failed: %s", e)

        return [
            {
                "id": r.id,
                "source_item_id": r.source_item_id,
                "target_item_id": r.target_item_id,
                "source_domain": r.source_domain,
                "target_domain": r.target_domain,
                "bridge_type": r.bridge_type,
                "shared_concept": r.shared_concept,
                "confidence": r.confidence,
                "description": r.description
            }
            for r in self._in_memory_connections
        ]

    def accumulate_item(self, item: Any) -> None:
        """Accumulates an ExtractedEvidenceItem or structured knowledge item into cache."""
        stmt = getattr(item, "statement", str(item))
        rec = AccumulatedKnowledgeRecord(
            id=getattr(item, "item_id", f"accum-{uuid.uuid4().hex[:12]}"),
            document_id=getattr(item, "source_name", "evidence"),
            source_name=getattr(item, "source_name", "literature"),
            source_title=getattr(item, "source_title", "evidence"),
            doi=getattr(item, "doi", None),
            domain="physics",
            item_type=getattr(item, "item_type", "fact"),
            content=stmt,
            canonical_symbol=getattr(item, "canonical_symbol", None),
            variables=getattr(item, "variables", {}) or {},
            confidence=getattr(item, "confidence", 0.95),
        )
        self._in_memory_items.append(rec)

    def get_bridges(self) -> List[Any]:
        """Returns in-memory cross-domain connection bridges."""
        return list(self._in_memory_connections)
