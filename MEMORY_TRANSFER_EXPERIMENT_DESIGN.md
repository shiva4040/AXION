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
    "title": "Hagen-Poiseuille Viscous Hydraulic Flow Resistance",
    "statement": "The volumetric hydraulic flow resistance in a circular conduit under laminar, fully developed Newtonian flow is R_hyd = (8 * mu * L) / (pi * r^4).",
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
    "conditions": ["laminar_flow", "Reynolds_number < 2100", "circular_cross_section", "rigid_walls"],
    "assumptions": ["incompressible_fluid", "no_slip_boundary", "steady_state"],
    "limitations": ["Inapplicable to turbulent regimes (Re >= 2100)", "Inapplicable to non-Newtonian slurries"],
    "permitted_applicability_range": {
      "Reynolds_number": { "min": 0.0, "max": 2100.0, "unit": "dimensionless" },
      "pipe_radius": { "min": 1e-6, "max": 0.5, "unit": "m" }
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
    "title": "Fourier Linear Thermal Conduction Resistance",
    "statement": "The one-dimensional steady-state conductive thermal resistance across a planar slab of area A and thickness L is R_th = L / (k * A).",
    "source_evidence": "doc-seed-thermo-physics-p45",
    "equations": ["R_th = L / (k * A)", "Delta_T = q_flux * R_th"],
    "variables": {
      "R_th": "[M]-1[L]-2[T]3[Theta]1",
      "k": "[M][L]1[T]-3[Theta]-1",
      "A": "[L]2",
      "L": "[L]",
      "Delta_T": "[Theta]",
      "q_flux": "[M][L]2[T]-3"
    },
    "conditions": ["steady_state", "1D_heat_flux", "isotropic_conductivity"],
    "assumptions": ["temperature_independent_k", "no_internal_generation"],
    "limitations": ["Inapplicable to transient thermal spikes", "Inapplicable to radiative boundary dominance"],
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
    "title": "Ideal Gas Mechanical Isothermal Compression Work",
    "statement": "The mechanical work required to reversibly compress n moles of an ideal gas from V_1 to V_2 at constant temperature T is W = n * R_gas * T * ln(V_1 / V_2).",
    "source_evidence": "doc-seed-thermo-physics-p67",
    "equations": ["W = n * R_gas * T * log(V_1 / V_2)"],
    "variables": {
      "W": "[M][L]2[T]-2",
      "n": "[N]",
      "R_gas": "[M][L]2[T]-2[Theta]-1[N]-1",
      "T": "[Theta]",
      "V_1": "[L]3",
      "V_2": "[L]3"
    },
    "conditions": ["isothermal_process", "ideal_gas_behavior", "reversible_quasistatic"],
    "assumptions": ["negligible_intermolecular_forces", "equilibrium_at_all_states"],
    "limitations": ["Inapplicable near critical point or high pressure (P > 50 atm)"],
    "permitted_applicability_range": {
      "pressure": { "min": 1e3, "max": 5e6, "unit": "Pa" }
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
