import uuid
import networkx as nx
from typing import Optional, List, Dict, Any
from axion.core.provider import LLMProvider, ChatMessage, get_llm_provider
from axion.reasoning.types import SubProblem, DependencyEdge, ReasoningDAG, SubProblemStatus

class GoalDecomposer:
    """
    Component 5 Subsystem:
    Decomposes compound scientific or engineering goals into a Directed Acyclic Graph (DAG)
    of sub-problems and required premises.
    """
    def __init__(self, provider: Optional[LLMProvider] = None):
        self.provider = provider or get_llm_provider()

    def _heuristic_decompose(self, goal: str) -> ReasoningDAG:
        """
        Deterministic, rule-based decomposition for physics, energy, and engineering problems.
        Ensures unit tests run deterministically and fast without external LLM dependencies.
        """
        problem_id = str(uuid.uuid4())
        sub_problems: Dict[str, SubProblem] = {}
        dependencies: List[DependencyEdge] = []

        g_lower = goal.lower()

        if "vehicle" in g_lower or "solar" in g_lower or "car" in g_lower:
            # Multi-physics Solar EV decomposition
            sp1 = SubProblem(
                id="sp_1_aero_roll",
                order=1,
                title="Calculate Mechanical Road Load Resistance",
                description="Determine aerodynamic drag force and rolling resistance across vehicle velocity.",
                target_domain="eng:mechanical_kinematics",
                required_variables=["v", "c_d", "c_rr", "mass", "f_drag", "f_roll"],
                equations_to_evaluate=["f = f_drag + f_roll"]
            )
            sp2 = SubProblem(
                id="sp_2_motor_demand",
                order=2,
                title="Determine Powertrain Power Demand",
                description="Calculate required mechanical and electrical motor power: P = F * v / eta_motor.",
                target_domain="eng:electrical_powertrain",
                required_variables=["f", "v", "p_demand", "eta"],
                equations_to_evaluate=["p = f * v"]
            )
            sp3 = SubProblem(
                id="sp_3_solar_gen",
                order=3,
                title="Compute Solar Photovoltaic Generation",
                description="Calculate peak solar power captured from available vehicle surface area: P_pv = Area * G * eta_pv.",
                target_domain="physics:photovoltaics",
                required_variables=["area", "p_solar", "eta_pv"],
                equations_to_evaluate=["p_solar = area * 1000.0 * eta_pv"]
            )
            sp4 = SubProblem(
                id="sp_4_energy_balance",
                order=4,
                title="Evaluate Energy Balance & Storage Deficit",
                description="Compare generation against demand to detect energy deficit or sizing requirements.",
                target_domain="eng:systems_energy",
                required_variables=["p_solar", "p_demand"],
                equations_to_evaluate=["p_solar = p_demand"]
            )

            sub_problems = {
                sp1.id: sp1,
                sp2.id: sp2,
                sp3.id: sp3,
                sp4.id: sp4
            }

            dependencies = [
                DependencyEdge(from_subproblem_id=sp1.id, to_subproblem_id=sp2.id, dependency_type="PROVIDES_FORCE"),
                DependencyEdge(from_subproblem_id=sp2.id, to_subproblem_id=sp4.id, dependency_type="PROVIDES_DEMAND"),
                DependencyEdge(from_subproblem_id=sp3.id, to_subproblem_id=sp4.id, dependency_type="PROVIDES_GENERATION")
            ]

        else:
            # Generic 2-stage scientific inquiry
            sp1 = SubProblem(
                id="sp_1_gather_premises",
                order=1,
                title="Identify Core Governing Laws and Parameters",
                description=f"Extract primary scientific equations governing: {goal[:60]}",
                target_domain="general_science",
                required_variables=[]
            )
            sp2 = SubProblem(
                id="sp_2_evaluate_solution",
                order=2,
                title="Evaluate Constraints and Calculate Target",
                description="Check dimensional consistency and solve for target variables.",
                target_domain="general_science",
                required_variables=[]
            )
            sub_problems = {sp1.id: sp1, sp2.id: sp2}
            dependencies = [
                DependencyEdge(from_subproblem_id=sp1.id, to_subproblem_id=sp2.id, dependency_type="REQUIRES_PREMISES")
            ]

        # Verify DAG with NetworkX and compute topological sort order
        G = nx.DiGraph()
        for sp_id in sub_problems:
            G.add_node(sp_id)
        for dep in dependencies:
            G.add_edge(dep.from_subproblem_id, dep.to_subproblem_id)

        is_dag = nx.is_directed_acyclic_graph(G)
        order = list(nx.topological_sort(G)) if is_dag else list(sub_problems.keys())

        return ReasoningDAG(
            problem_id=problem_id,
            goal=goal,
            sub_problems=sub_problems,
            dependencies=dependencies,
            topological_order=order,
            is_acyclic=is_dag
        )

    async def decompose(self, goal: str) -> ReasoningDAG:
        """
        Decomposes a user goal into an acyclic reasoning graph.
        """
        from axion.core.provider import MockProvider
        if isinstance(self.provider, MockProvider):
            return self._heuristic_decompose(goal)

        # LLM-assisted decomposition
        prompt = f"""
Decompose this scientific or technical problem into an acyclic dependency graph of 2 to 5 sub-problems.
Return JSON:
{{
  "sub_problems": [
    {{"id": "sp_1", "order": 1, "title": "...", "description": "...", "target_domain": "...", "required_variables": ["..."], "equations_to_evaluate": ["..."]}}
  ],
  "dependencies": [
    {{"from_subproblem_id": "sp_1", "to_subproblem_id": "sp_2"}}
  ]
}}
Goal: {goal}
"""
        messages = [
            ChatMessage(role="system", content="You are an expert scientific problem decomposition engine. Output strictly valid JSON."),
            ChatMessage(role="user", content=prompt)
        ]
        resp = await self.provider.generate_text(messages=messages, temperature=0.0)
        try:
            import json
            data = json.loads(resp.text)
            sub_problems = {item["id"]: SubProblem(**item) for item in data["sub_problems"]}
            dependencies = [DependencyEdge(**dep) for dep in data.get("dependencies", [])]

            G = nx.DiGraph()
            for sp_id in sub_problems:
                G.add_node(sp_id)
            for dep in dependencies:
                G.add_edge(dep.from_subproblem_id, dep.to_subproblem_id)

            is_dag = nx.is_directed_acyclic_graph(G)
            order = list(nx.topological_sort(G)) if is_dag else list(sub_problems.keys())

            return ReasoningDAG(
                problem_id=str(uuid.uuid4()),
                goal=goal,
                sub_problems=sub_problems,
                dependencies=dependencies,
                topological_order=order,
                is_acyclic=is_dag
            )
        except Exception:
            return self._heuristic_decompose(goal)
