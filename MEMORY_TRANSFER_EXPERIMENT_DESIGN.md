# AXION — Memory Transfer Experiment Design Specification

**Document Version:** 1.0.0  
**Phase Target:** Phase 0 Experimental Protocol  
**System Scope:** Stage 07 (Verified Findings Memory) & Stage 04 (Transfer Engine)  
**Date:** November 19, 2026  

---

## 1. Experimental Objective & Central Hypothesis

The purpose of this experiment is to evaluate whether persistent storage of structured **Verified Findings** accelerates problem solving and enables cross-domain transfer without causing epistemic degradation or false transfers.

### Core Research Questions
1. Does retrieving previously verified findings improve accuracy and reduce calculation latency on unfamiliar multi-disciplinary problems compared to AXION without memory?
2. Does the Stage 06 Applicability Guard reliably prevent **False Transfers** (applying a verified finding outside its valid conditions, assumptions, or dimensional ranges)?

---

## 2. Seed Set of Verified Findings

A fixed seed set of 6 foundational verified findings is established prior to evaluation. These findings represent knowledge previously validated through Stage 06 verification. **None of these seed findings are derived from locked test questions.**

```json
[
  {
    "finding_id": "FIND-SEED-001",
    "title": "Hagen-Poiseuille Viscous Hydraulic Flow Resistance (Fully Developed Laminar Flow)",
    "statement": "In fully developed, steady, laminar flow of an incompressible Newtonian fluid through a straight circular conduit of radius r and length L, the volumetric hydraulic flow resistance is R_hyd = (8 * mu * L) / (pi * r^4), and the resulting viscous pressure drop is Delta_P = Q * R_hyd.",
    "source_evidence": "doc-seed-fluid-dynamics-p12",
    "equations": ["R_hyd = (8 * mu * L) / (pi * r**4)", "Delta_P = Q * R_hyd"],
    "variables": {
      "R_hyd": "[M][L]-4[T]-1",
      "mu": "[M][L]-1[T]-1",
      "L": "[L]",
      "r": "[L]",
      "Delta_P": "[M][L]-1[T]-2",
      "Q": "[L]3[T]-1"
    },
    "conditions": [
      "laminar_flow (Reynolds_number < 2100)",
      "Newtonian_fluid_behavior (constant dynamic viscosity mu)",
      "circular_cross_section_uniform_bore",
      "rigid_conduit_walls (zero elasticity)",
      "fully_developed_flow (hydrodynamic entrance length satisfied: L / D >= 0.05 * Re to 0.06 * Re as reference-dependent engineering estimate)"
    ],
    "assumptions": [
      "steady_state_flow (zero time-dependent acceleration)",
      "incompressible_fluid (constant density)",
      "no_slip_boundary_at_wall",
      "isothermal_viscosity (negligible viscous self-heating)"
    ],
    "limitations": [
      "Inapplicable to turbulent regimes (Re >= 2100)",
      "Inapplicable to non-Newtonian fluids (blood in microvessels, polymer solutions, slurries)",
      "Inapplicable to entrance-region flow (L / D < 0.05 * Re) where Hagenbach pressure loss correction is required",
      "Inapplicable to compliant/elastic biological vessels"
    ],
    "permitted_applicability_range": {
      "Reynolds_number": { "min": 0.0, "max": 2100.0, "unit": "dimensionless" },
      "pipe_radius": { "min": 1e-6, "max": 0.5, "unit": "m" },
      "aspect_ratio_L_over_D": { "min": 10.0, "max": 1e6, "unit": "dimensionless" }
    },
    "verification_record": {
      "verified_by": "Stage06_HypothesisTester",
      "experiment_id": "exp-seed-audit-001",
      "verdict": "VERIFIED_SUPPORTED",
      "confidence": 0.99
    }
  },
  {
    "finding_id": "FIND-SEED-002",
    "title": "Fourier Linear Conductive Thermal Resistance",
    "statement": "The one-dimensional steady-state conductive thermal resistance across a planar slab of area A, thickness L, and thermal conductivity k is R_th = L / (k * A). The temperature drop across the slab is Delta_T = Q_heat_rate * R_th, where Q_heat_rate is the total heat-transfer rate in Watts.",
    "source_evidence": "doc-seed-thermo-physics-p45",
    "equations": ["R_th = L / (k * A)", "Delta_T = Q_heat_rate * R_th"],
    "variables": {
      "R_th": "[M]-1[L]-2[T]3[Theta]1",
      "k": "[M][L]1[T]-3[Theta]-1",
      "A": "[L]2",
      "L": "[L]",
      "Delta_T": "[Theta]",
      "Q_heat_rate": "[M][L]2[T]-3"
    },
    "conditions": [
      "steady_state_thermal_conduction",
      "1D_perpendicular_heat_flow",
      "isotropic_thermal_conductivity"
    ],
    "assumptions": [
      "temperature_independent_thermal_conductivity_k",
      "zero_internal_heat_generation",
      "constant_cross_sectional_area_A"
    ],
    "limitations": [
      "Inapplicable to transient thermal spikes or dynamic heating",
      "Inapplicable to radiative boundary dominance or high convective Biot numbers",
      "Distinguishes heat-transfer rate Q_heat_rate (Watts) from heat flux density q'' (W/m^2)"
    ],
    "permitted_applicability_range": {
      "temperature_kelvin": { "min": 50.0, "max": 800.0, "unit": "K" }
    },
    "verification_record": {
      "verified_by": "Stage06_HypothesisTester",
      "experiment_id": "exp-seed-audit-002",
      "verdict": "VERIFIED_SUPPORTED",
      "confidence": 0.99
    }
  },
  {
    "finding_id": "FIND-SEED-003",
    "title": "Ohmic Electrical Conductive Dissipation",
    "statement": "The electric potential drop across a linear ohmic conductor of resistivity rho, length L, and cross-section A is V = I * (rho * L / A).",
    "source_evidence": "doc-seed-electrodynamics-p08",
    "equations": ["R_elec = (rho * L) / A", "V = I * R_elec"],
    "variables": {
      "R_elec": "[M][L]2[T]-3[I]-2",
      "rho": "[M][L]3[T]-3[I]-2",
      "L": "[L]",
      "A": "[L]2",
      "V": "[M][L]2[T]-3[I]-1",
      "I": "[I]"
    },
    "conditions": ["ohmic_material", "isothermal_conductor", "steady_state_dc"],
    "assumptions": ["uniform_current_density", "negligible_skin_effect"],
    "limitations": ["Inapplicable at high RF frequencies", "Inapplicable to superconductors or plasma"],
    "permitted_applicability_range": {
      "current_density": { "min": 0.0, "max": 1e7, "unit": "A/m^2" }
    },
    "verification_record": {
      "verified_by": "Stage06_HypothesisTester",
      "experiment_id": "exp-seed-audit-003",
      "verdict": "VERIFIED_SUPPORTED",
      "confidence": 0.99
    }
  },
  {
    "finding_id": "FIND-SEED-004",
    "title": "Capacitive Electrostatic Energy Storage",
    "statement": "The electrostatic potential energy stored in an ideal dielectric capacitor of capacitance C charged to potential V is E_cap = 0.5 * C * V^2.",
    "source_evidence": "doc-seed-electrodynamics-p31",
    "equations": ["E_cap = 0.5 * C * V**2"],
    "variables": {
      "E_cap": "[M][L]2[T]-2",
      "C": "[M]-1[L]-2[T]4[I]2",
      "V": "[M][L]2[T]-3[I]-1"
    },
    "conditions": ["electrostatic_equilibrium", "linear_dielectric", "voltage_below_breakdown"],
    "assumptions": ["negligible_leakage_current", "negligible_fringing_fields"],
    "limitations": ["Inapplicable above dielectric breakdown field E_bd"],
    "permitted_applicability_range": {
      "electric_field": { "min": 0.0, "max": 3e6, "unit": "V/m" }
    },
    "verification_record": {
      "verified_by": "Stage06_HypothesisTester",
      "experiment_id": "exp-seed-audit-004",
      "verdict": "VERIFIED_SUPPORTED",
      "confidence": 0.99
    }
  },
  {
    "finding_id": "FIND-SEED-005",
    "title": "Ideal Gas Mechanical Isothermal Compression & Expansion Work",
    "statement": "The mechanical work done ON an ideal gas system to reversibly and isothermally compress n moles from initial volume V_1 to final volume V_2 (where V_1 > V_2) at constant temperature T is W_on = n * R_gas * T * ln(V_1 / V_2). Conversely, the work done BY the expanding gas on the surroundings is W_by = -W_on = n * R_gas * T * ln(V_2 / V_1).",
    "source_evidence": "doc-seed-thermo-physics-p67",
    "equations": [
      "W_on = n * R_gas * T * log(V_1 / V_2)",
      "W_by = n * R_gas * T * log(V_2 / V_1)"
    ],
    "variables": {
      "W_on": "[M][L]2[T]-2",
      "W_by": "[M][L]2[T]-2",
      "n": "[N]",
      "R_gas": "[M][L]2[T]-2[Theta]-1[N]-1",
      "T": "[Theta]",
      "V_1": "[L]3",
      "V_2": "[L]3"
    },
    "conditions": [
      "isothermal_process (constant temperature T)",
      "ideal_gas_behavior (obeying P * V = n * R_gas * T)",
      "reversible_quasistatic_compression_or_expansion"
    ],
    "assumptions": [
      "negligible_intermolecular_potential_forces",
      "thermodynamic_equilibrium_at_all_intermediate_states",
      "sign_convention_explicitly_declared (W_on > 0 for compression where V_1 > V_2; W_by > 0 for expansion where V_2 > V_1)"
    ],
    "limitations": [
      "Inapplicable near the gas-liquid critical point or high pressures (P > 50 atm)",
      "Inapplicable to fast irreversible adiabatic or non-quasistatic throttling processes"
    ],
    "permitted_applicability_range": {
      "pressure": { "min": 1e3, "max": 5e6, "unit": "Pa" },
      "temperature_kelvin": { "min": 150.0, "max": 1200.0, "unit": "K" }
    },
    "verification_record": {
      "verified_by": "Stage06_HypothesisTester",
      "experiment_id": "exp-seed-audit-005",
      "verdict": "VERIFIED_SUPPORTED",
      "confidence": 0.99
    }
  },
  {
    "finding_id": "FIND-SEED-006",
    "title": "First-Order Biochemical Michaelis-Menten Low-Substrate Approximation",
    "statement": "When substrate concentration S is much smaller than the Michaelis constant K_m (S << K_m), reaction velocity simplifies to v_rxn = (V_max / K_m) * S.",
    "source_evidence": "doc-seed-biochem-p88",
    "equations": ["v_rxn = (V_max / K_m) * S"],
    "variables": {
      "v_rxn": "[N][L]-3[T]-1",
      "V_max": "[N][L]-3[T]-1",
      "K_m": "[N][L]-3",
      "S": "[N][L]-3"
    },
    "conditions": ["pseudo_steady_state", "S << K_m", "constant_enzyme_concentration"],
    "assumptions": ["no_allosteric_inhibition", "reversible_binding"],
    "limitations": ["Inapplicable when substrate saturates (S >= 0.1 * K_m)"],
    "permitted_applicability_range": {
      "substrate_ratio": { "min": 0.0, "max": 0.05, "unit": "dimensionless" }
    },
    "verification_record": {
      "verified_by": "Stage06_HypothesisTester",
      "experiment_id": "exp-seed-audit-006",
      "verdict": "VERIFIED_SUPPORTED",
      "confidence": 0.99
    }
  }
]
```

---

## 3. Structured Question Order & Test Cases

The evaluation executes in a strict deterministic sequence across 30 questions designed to probe specific memory dynamics:

| Question Range | Test Condition Type | Description & Expected Mechanism |
| :--- | :--- | :--- |
| **Q01 – Q06** | **Legitimate Reuse (Positive)** | Problems where target conditions strictly match seed finding (e.g. microchannel capillary flow where $\text{Re} = 120 < 2100$). Memory should be retrieved, validated, and directly solved. |
| **Q07 – Q12** | **Inapplicable Reuse (Negative)** | Target problem resembles seed finding but deliberately violates an essential boundary (e.g. turbulent gas exhaust where $\text{Re} = 15,000$). **Stage 06 MUST reject transfer.** |
| **Q13 – Q18** | **Multi-Finding Composition** | Problem requires chaining two distinct findings (e.g. combining electrical dissipation `FIND-SEED-003` with thermal conduction `FIND-SEED-002` to determine steady-state wire core temperature). |
| **Q19 – Q24** | **Missing Condition Abstention** | Target problem omits Reynolds number or temperature regime. System must identify that conditions are indeterminate and refuse to assume validity. |
| **Q25 – Q30** | **Unseen Cross-Domain Analogy** | Analogical mapping to an entirely novel domain (e.g. applying hydraulic resistance `FIND-SEED-001` to vascular blood flow in a biomedical micro-artery). |

---

## 4. Quantitative Evaluation Metrics for Memory

We define five rigorous metrics to assess memory utility:

1. **Memory Reuse Rate ($R_{\text{reuse}}$):**
   $$R_{\text{reuse}} = \frac{N_{\text{retrieved\_and\_accepted}}}{N_{\text{applicable\_questions}}}$$
2. **Transfer Accuracy ($A_{\text{transfer}}$):**
   $$A_{\text{transfer}} = \frac{N_{\text{correct\_solutions\_with\_memory}}}{N_{\text{applicable\_questions}}}$$
3. **False-Transfer Rate ($R_{\text{false\_transfer}}$) [Critical Safety Metric]:**
   $$R_{\text{false\_transfer}} = \frac{N_{\text{inapplicable\_findings\_erroneously\_accepted}}}{N_{\text{inapplicable\_questions}}}$$
   *Acceptance Criterion:* $R_{\text{false\_transfer}} = 0.00$ (Zero tolerance for accepting invalid physical analogies).
4. **Correct Rejection Rate ($R_{\text{correct\_rejection}}$):**
   $$R_{\text{correct\_rejection}} = \frac{N_{\text{inapplicable\_findings\_correctly\_blocked}}}{N_{\text{inapplicable\_questions}}}$$
5. **Net Memory Differential ($\Delta_{\text{mem}}$):**
   $$\Delta_{\text{mem}} = \text{Score}(\text{AXION}_{\text{with\_memory}}) - \text{Score}(\text{AXION}_{\text{no\_memory}})$$
