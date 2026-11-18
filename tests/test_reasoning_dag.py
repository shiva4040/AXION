import pytest
import networkx as nx
from axion.reasoning.decomposer import GoalDecomposer
from axion.reasoning.types import ReasoningDAG, SubProblemStatus

@pytest.mark.asyncio
async def test_goal_decomposition_solar_ev():
    decomposer = GoalDecomposer()
    goal = "Design a small solar-powered electric vehicle with a 75 kg rider"
    dag: ReasoningDAG = await decomposer.decompose(goal)

    assert dag.is_acyclic is True
    assert len(dag.sub_problems) == 4
    assert len(dag.dependencies) >= 3

    # Check topological order: sp_1 (road load) must precede sp_2 (motor demand)
    order = dag.topological_order
    assert order.index("sp_1_aero_roll") < order.index("sp_2_motor_demand")
    # sp_2 (demand) and sp_3 (solar generation) must precede sp_4 (energy balance)
    assert order.index("sp_2_motor_demand") < order.index("sp_4_energy_balance")
    assert order.index("sp_3_solar_gen") < order.index("sp_4_energy_balance")

    # Check variable specifications
    sp1 = dag.sub_problems["sp_1_aero_roll"]
    assert "v" in sp1.required_variables
    assert "f_drag" in sp1.required_variables
    assert sp1.target_domain == "eng:mechanical_kinematics"

@pytest.mark.asyncio
async def test_goal_decomposition_generic_problem():
    decomposer = GoalDecomposer()
    goal = "Investigate the superconducting critical temperature in high-entropy alloys"
    dag: ReasoningDAG = await decomposer.decompose(goal)

    assert dag.is_acyclic is True
    assert len(dag.sub_problems) >= 2
    assert len(dag.topological_order) >= 2
