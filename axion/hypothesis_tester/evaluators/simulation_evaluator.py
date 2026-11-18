import math
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from axion.hypothesis_tester.types import ExperimentVerdict, SimulationResult

class SimulationEvaluator:
    """
    Executes numerical ODE simulations (Runge-Kutta 4th order) of dynamical models:
    - 1st order decay / cooling / charging: dx/dt = -k*(x - x_target)
    - 2nd order damped oscillator / RLC circuit: d2x/dt2 + 2*zeta*w0*dx/dt + w0^2*x = 0
    - Checks stability, transient decay, steady-state convergence, and divergence.
    """

    def simulate_dynamical_hypothesis(
        self,
        system_type: str, # "first_order_decay" or "second_order_oscillator"
        parameters: Dict[str, float],
        initial_conditions: Dict[str, float],
        time_span: Tuple[float, float] = (0.0, 10.0),
        step_size: float = 0.05,
        expected_steady_state: Optional[Dict[str, float]] = None,
        tolerance: float = 0.10,
    ) -> Tuple[ExperimentVerdict, SimulationResult, Dict[str, Any], Optional[str]]:
        t_start, t_end = time_span
        if t_end <= t_start or step_size <= 0:
            return (
                ExperimentVerdict.INSUFFICIENT_DATA,
                SimulationResult(converged=False),
                {},
                "Invalid time span or step size for numerical simulation."
            )

        steps = int((t_end - t_start) / step_size)
        t_points = [round(t_start + i * step_size, 4) for i in range(steps + 1)]

        if system_type == "first_order_decay":
            # dx/dt = -k * (x - x_env)
            k = float(parameters.get("k", 1.0))
            x_env = float(parameters.get("x_env", 0.0))
            x_val = float(initial_conditions.get("x", 1.0))

            x_traj = [x_val]
            divergence = False

            for _ in range(steps):
                # RK4 for dx/dt = -k * (x - x_env)
                f = lambda x: -k * (x - x_env)
                k1 = f(x_val)
                k2 = f(x_val + 0.5 * step_size * k1)
                k3 = f(x_val + 0.5 * step_size * k2)
                k4 = f(x_val + step_size * k3)
                x_val += (step_size / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)

                if math.isnan(x_val) or math.isinf(x_val) or abs(x_val) > 1e9:
                    divergence = True
                    break
                x_traj.append(round(x_val, 6))

            sim_res = SimulationResult(
                time_points=t_points[:len(x_traj)],
                state_trajectories={"x": x_traj},
                steady_state_values={"x": round(x_traj[-1], 6)},
                converged=not divergence,
                step_count=len(x_traj),
                divergence_detected=divergence,
            )

            if divergence:
                return (
                    ExperimentVerdict.NOT_SUPPORTED,
                    sim_res,
                    {"divergence": True},
                    "Numerical simulation diverged (exponential instability detected)."
                )

            # Check steady state expectation
            if expected_steady_state and "x" in expected_steady_state:
                exp_x = expected_steady_state["x"]
                actual_x = x_traj[-1]
                err = abs(actual_x - exp_x) / max(abs(exp_x), 1e-6)
                if err <= tolerance:
                    return (
                        ExperimentVerdict.SUPPORTED,
                        sim_res,
                        {"final_x": actual_x, "relative_error": round(err, 4)},
                        None
                    )
                else:
                    return (
                        ExperimentVerdict.NOT_SUPPORTED,
                        sim_res,
                        {"final_x": actual_x, "relative_error": round(err, 4)},
                        f"Steady-state mismatch: expected {exp_x}, simulated {actual_x} (error {err:.2%})."
                    )

            return ExperimentVerdict.SUPPORTED, sim_res, {"final_x": x_traj[-1]}, None

        elif system_type == "second_order_oscillator":
            # State vector [x, v]: dx/dt = v, dv/dt = -2*zeta*w0*v - w0^2*x
            w0 = float(parameters.get("w0", parameters.get("omega0", 1.0)))
            zeta = float(parameters.get("zeta", 0.1))
            x_val = float(initial_conditions.get("x", 1.0))
            v_val = float(initial_conditions.get("v", 0.0))

            x_traj = [x_val]
            v_traj = [v_val]
            divergence = False

            for _ in range(steps):
                # RK4 on 2D system
                def derivs(x, v):
                    return v, -2.0 * zeta * w0 * v - (w0 ** 2) * x

                dx1, dv1 = derivs(x_val, v_val)
                dx2, dv2 = derivs(x_val + 0.5 * step_size * dx1, v_val + 0.5 * step_size * dv1)
                dx3, dv3 = derivs(x_val + 0.5 * step_size * dx2, v_val + 0.5 * step_size * dv2)
                dx4, dv4 = derivs(x_val + step_size * dx3, v_val + step_size * dv3)

                x_val += (step_size / 6.0) * (dx1 + 2 * dx2 + 2 * dx3 + dx4)
                v_val += (step_size / 6.0) * (dv1 + 2 * dv2 + 2 * dv3 + dv4)

                if math.isnan(x_val) or math.isinf(x_val) or abs(x_val) > 1e9:
                    divergence = True
                    break
                x_traj.append(round(x_val, 6))
                v_traj.append(round(v_val, 6))

            sim_res = SimulationResult(
                time_points=t_points[:len(x_traj)],
                state_trajectories={"x": x_traj, "v": v_traj},
                steady_state_values={"x": round(x_traj[-1], 6), "v": round(v_traj[-1], 6)},
                converged=not divergence,
                step_count=len(x_traj),
                divergence_detected=divergence,
            )

            if divergence:
                return (
                    ExperimentVerdict.NOT_SUPPORTED,
                    sim_res,
                    {"divergence": True},
                    "Second-order dynamical simulation diverged into unbounded growth."
                )

            # For damped oscillator, energy must decay if zeta > 0
            if zeta > 0:
                initial_energy = 0.5 * (v_traj[0]**2 + (w0 * x_traj[0])**2)
                final_energy = 0.5 * (v_traj[-1]**2 + (w0 * x_traj[-1])**2)
                if final_energy > initial_energy + 1e-4:
                    return (
                        ExperimentVerdict.NOT_SUPPORTED,
                        sim_res,
                        {"initial_energy": initial_energy, "final_energy": final_energy},
                        "Violation of physical dissipation: simulated energy increased in damped oscillator."
                    )

            return ExperimentVerdict.SUPPORTED, sim_res, {"final_x": x_traj[-1], "final_v": v_traj[-1]}, None

        else:
            return (
                ExperimentVerdict.INSUFFICIENT_DATA,
                SimulationResult(converged=False),
                {},
                f"Unsupported dynamical system type: {system_type}"
            )
