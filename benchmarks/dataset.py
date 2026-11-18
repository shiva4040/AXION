from typing import List
from axion.core.types import EntityCategory, EpistemicTier, RelationType, ProvenancePointer
from axion.transfer.types import (
    ApplicabilityVerdict,
    BoundaryConstraint,
    DomainConcept,
    DomainKnowledgeBundle,
    DomainRelation,
)
from benchmarks.types import BenchmarkProblem, ProblemTier

def create_bundle(
    domain_name: str,
    concepts_raw: List[dict],
    relations_raw: List[dict],
    assumptions: List[str] = None,
    boundary_conditions: List[dict] = None,
) -> DomainKnowledgeBundle:
    concepts = [
        DomainConcept(
            name=c["name"],
            domain=domain_name,
            category=c.get("category", EntityCategory.CONCEPT),
            symbol=c.get("symbol"),
            si_dimension=c.get("si_dimension"),
            role=c.get("role"),
            provenance=ProvenancePointer(
                document_id="doc-synthetic-bench",
                chunk_id="chk-001",
                page_number=1,
                extracted_snippet=f"{c['name']} defined in {domain_name}."
            )
        )
        for c in concepts_raw
    ]
    relations = [
        DomainRelation(
            source_concept=r["source"],
            target_concept=r["target"],
            relation_type=r.get("type", RelationType.GOVERNED_BY),
            equation=r.get("equation"),
            epistemic_tier=r.get("tier", EpistemicTier.FACT_DOCUMENTED),
            assumptions_required=r.get("assumptions", []),
            provenance=ProvenancePointer(
                document_id="doc-synthetic-bench",
                chunk_id="chk-001",
                page_number=1,
                extracted_snippet=r.get("snippet", f"{r['source']} relates to {r['target']}.")
            )
        )
        for r in relations_raw
    ]
    bcs = [
        BoundaryConstraint(
            variable_name=b["variable"],
            min_value=b.get("min"),
            max_value=b.get("max"),
            unit=b.get("unit"),
            description=b.get("desc")
        )
        for b in (boundary_conditions or [])
    ]
    return DomainKnowledgeBundle(
        domain_name=domain_name,
        concepts=concepts,
        relations=relations,
        assumptions=assumptions or [],
        boundary_conditions=bcs
    )

def get_benchmark_dataset() -> List[BenchmarkProblem]:
    problems: List[BenchmarkProblem] = []

    # =========================================================================
    # TIER E: 10 Easy Single-Domain Problems
    # =========================================================================
    # E01: Electrical Ohm's Law
    b_elec = create_bundle(
        "physics:electromagnetism",
        [
            {"name": "Electric Voltage", "symbol": "V", "role": "potential", "si_dimension": "[M][L]2[T]-3[I]-1"},
            {"name": "Electric Current", "symbol": "I", "role": "flux", "si_dimension": "[I]"},
            {"name": "Electrical Resistance", "symbol": "R", "role": "resistance", "si_dimension": "[M][L]2[T]-3[I]-2"},
        ],
        [{"source": "Electric Voltage", "target": "Electric Current", "type": RelationType.PROPORTIONAL_TO, "equation": "V = I * R", "assumptions": ["ohmic_conduction", "steady_state"]}],
        assumptions=["ohmic_conduction", "steady_state"]
    )
    problems.append(BenchmarkProblem(
        problem_id="E01",
        tier=ProblemTier.TIER_E,
        title="Ohm's Law Potential-Flux Relationship",
        query="What is the relation between electric voltage and electric current in an ohmic conductor?",
        domains=[b_elec],
        ground_truth_answer="Electric voltage is directly proportional to electric current through electrical resistance: V = I * R.",
        tags=["single_domain", "electricity"]
    ))

    # E02: Fourier's Law
    b_thermal = create_bundle(
        "physics:thermodynamics",
        [
            {"name": "Temperature Gradient", "symbol": "dT_dx", "role": "potential", "si_dimension": "[Θ][L]-1"},
            {"name": "Heat Flux", "symbol": "q", "role": "flux", "si_dimension": "[M][T]-3"},
            {"name": "Thermal Conductivity", "symbol": "k", "role": "diffusivity", "si_dimension": "[M][L][T]-3[Θ]-1"},
        ],
        [{"source": "Temperature Gradient", "target": "Heat Flux", "type": RelationType.PROPORTIONAL_TO, "equation": "q = -k * dT_dx", "assumptions": ["linear", "steady_state"]}],
        assumptions=["linear", "steady_state"]
    )
    problems.append(BenchmarkProblem(
        problem_id="E02",
        tier=ProblemTier.TIER_E,
        title="Fourier's Law Heat Conduction",
        query="How is conductive heat flux governed by temperature gradient?",
        domains=[b_thermal],
        ground_truth_answer="Heat flux is directly proportional to temperature gradient: q = -k * dT / dx.",
        tags=["single_domain", "heat"]
    ))

    # E03: Fick's First Law
    b_diffusion = create_bundle(
        "physics:mass_transport",
        [
            {"name": "Concentration Gradient", "symbol": "dC_dx", "role": "potential", "si_dimension": "[N][L]-4"},
            {"name": "Mass Flux", "symbol": "J", "role": "flux", "si_dimension": "[N][L]-2[T]-1"},
            {"name": "Diffusion Coefficient", "symbol": "D", "role": "diffusivity", "si_dimension": "[L]2[T]-1"},
        ],
        [{"source": "Concentration Gradient", "target": "Mass Flux", "type": RelationType.PROPORTIONAL_TO, "equation": "J = -D * dC_dx", "assumptions": ["linear", "dilute_solution"]}],
        assumptions=["linear", "dilute_solution"]
    )
    problems.append(BenchmarkProblem(
        problem_id="E03",
        tier=ProblemTier.TIER_E,
        title="Fick's First Law Diffusion",
        query="What relates mass diffusive flux to concentration gradient?",
        domains=[b_diffusion],
        ground_truth_answer="Mass diffusive flux is proportional to concentration gradient: J = -D * dC_dx.",
        tags=["single_domain", "diffusion"]
    ))

    # E04: Hooke's Law
    b_elasticity = create_bundle(
        "mechanics:solid",
        [
            {"name": "Mechanical Force", "symbol": "F", "role": "driver", "si_dimension": "[M][L][T]-2"},
            {"name": "Spring Constant", "symbol": "k_spring", "role": "stiffness", "si_dimension": "[M][T]-2"},
            {"name": "Displacement", "symbol": "x", "role": "displacement", "si_dimension": "[L]"},
        ],
        [{"source": "Displacement", "target": "Mechanical Force", "type": RelationType.PROPORTIONAL_TO, "equation": "F = -k_spring * x", "assumptions": ["linear_elasticity"]}],
        assumptions=["linear_elasticity"]
    )
    problems.append(BenchmarkProblem(
        problem_id="E04",
        tier=ProblemTier.TIER_E,
        title="Hooke's Law Elastic Restitution",
        query="What is the restoring force of an ideal spring under displacement x?",
        domains=[b_elasticity],
        ground_truth_answer="Restoring force is linearly proportional to displacement: F = -k_spring * x.",
        tags=["single_domain", "mechanics"]
    ))

    # E05: Ideal Gas Law
    b_gas = create_bundle(
        "thermodynamics:gas",
        [
            {"name": "Gas Pressure", "symbol": "P", "role": "state", "si_dimension": "[M][L]-1[T]-2"},
            {"name": "Gas Temperature", "symbol": "T", "role": "state", "si_dimension": "[Θ]"},
            {"name": "Gas Volume", "symbol": "V_vol", "role": "state", "si_dimension": "[L]3"},
        ],
        [{"source": "Gas Temperature", "target": "Gas Pressure", "type": RelationType.PROPORTIONAL_TO, "equation": "P = n * R_gas * T / V_vol", "assumptions": ["ideal_gas"]}],
        assumptions=["ideal_gas"]
    )
    problems.append(BenchmarkProblem(
        problem_id="E05",
        tier=ProblemTier.TIER_E,
        title="Ideal Gas Pressure-Temperature Relation",
        query="How does gas pressure vary with temperature at constant volume for an ideal gas?",
        domains=[b_gas],
        ground_truth_answer="Pressure is directly proportional to absolute temperature.",
        tags=["single_domain", "ideal_gas"]
    ))

    # E06: Newton's Second Law
    b_dyn = create_bundle(
        "physics:mechanics",
        [
            {"name": "Net Force", "symbol": "F_net", "role": "force", "si_dimension": "[M][L][T]-2"},
            {"name": "Inertial Mass", "symbol": "m", "role": "inertia", "si_dimension": "[M]"},
            {"name": "Acceleration", "symbol": "a", "role": "kinematics", "si_dimension": "[L][T]-2"},
        ],
        [{"source": "Net Force", "target": "Acceleration", "type": RelationType.PROPORTIONAL_TO, "equation": "F_net = m * a", "assumptions": ["non_relativistic"]}],
        assumptions=["non_relativistic"]
    )
    problems.append(BenchmarkProblem(
        problem_id="E06",
        tier=ProblemTier.TIER_E,
        title="Newton's Second Law of Motion",
        query="What governs acceleration under an applied net force?",
        domains=[b_dyn],
        ground_truth_answer="Acceleration is proportional to net force and inversely proportional to inertial mass: F = m * a.",
        tags=["single_domain", "kinematics"]
    ))

    # E07: Poiseuille's Fluid Law
    b_fluid = create_bundle(
        "fluid_mechanics:pipe_flow",
        [
            {"name": "Pressure Drop", "symbol": "dP", "role": "potential", "si_dimension": "[M][L]-1[T]-2"},
            {"name": "Volumetric Flow Rate", "symbol": "Q_flow", "role": "flux", "si_dimension": "[L]3[T]-1"},
            {"name": "Hydraulic Resistance", "symbol": "R_h", "role": "resistance", "si_dimension": "[M][L]-4[T]-1"},
        ],
        [{"source": "Pressure Drop", "target": "Volumetric Flow Rate", "type": RelationType.PROPORTIONAL_TO, "equation": "dP = Q_flow * R_h", "assumptions": ["laminar_flow", "newtonian_fluid", "steady_state"]}],
        assumptions=["laminar_flow", "newtonian_fluid", "steady_state"]
    )
    problems.append(BenchmarkProblem(
        problem_id="E07",
        tier=ProblemTier.TIER_E,
        title="Poiseuille Laminar Pipe Flow",
        query="What relates pressure drop to volumetric flow rate in a circular laminar pipe?",
        domains=[b_fluid],
        ground_truth_answer="Volumetric flow rate is directly proportional to pressure drop across hydraulic resistance.",
        tags=["single_domain", "fluid"]
    ))

    # E08: Stefan-Boltzmann Law
    b_rad = create_bundle(
        "physics:radiation",
        [
            {"name": "Emissive Power", "symbol": "E_rad", "role": "flux", "si_dimension": "[M][T]-3"},
            {"name": "Surface Temperature", "symbol": "T_surf", "role": "potential", "si_dimension": "[Θ]"},
        ],
        [{"source": "Surface Temperature", "target": "Emissive Power", "type": RelationType.PROPORTIONAL_TO, "equation": "E_rad = sigma * T_surf**4", "assumptions": ["blackbody"]}],
        assumptions=["blackbody"]
    )
    problems.append(BenchmarkProblem(
        problem_id="E08",
        tier=ProblemTier.TIER_E,
        title="Stefan-Boltzmann Radiation Emission",
        query="How does thermal blackbody emissive power scale with surface temperature?",
        domains=[b_rad],
        ground_truth_answer="Emissive power scales with the fourth power of surface absolute temperature: E = sigma * T^4.",
        tags=["single_domain", "radiation"]
    ))

    # E09: Seebeck Effect
    b_seebeck = create_bundle(
        "physics:thermoelectrics",
        [
            {"name": "Open Circuit Voltage", "symbol": "V_oc", "role": "potential", "si_dimension": "[M][L]2[T]-3[I]-1"},
            {"name": "Temperature Differential", "symbol": "dT_junction", "role": "gradient", "si_dimension": "[Θ]"},
            {"name": "Seebeck Coefficient", "symbol": "S_coeff", "role": "coupling", "si_dimension": "[M][L]2[T]-3[I]-1[Θ]-1"},
        ],
        [{"source": "Temperature Differential", "target": "Open Circuit Voltage", "type": RelationType.PROPORTIONAL_TO, "equation": "V_oc = S_coeff * dT_junction", "assumptions": ["linear"]}],
        assumptions=["linear"]
    )
    problems.append(BenchmarkProblem(
        problem_id="E09",
        tier=ProblemTier.TIER_E,
        title="Seebeck Thermoelectric Voltage Generation",
        query="What voltage is generated across a thermoelectric material by a junction temperature difference?",
        domains=[b_seebeck],
        ground_truth_answer="Voltage is proportional to temperature difference via the Seebeck coefficient: V_oc = S * dT.",
        tags=["single_domain", "thermoelectric"]
    ))

    # E10: Synthetic Universe X1 Single-Domain Law
    b_syn1 = create_bundle(
        "synthetic:universe_x1",
        [
            {"name": "Quux Potential", "symbol": "Phi_q", "role": "potential", "si_dimension": "[M][L]2[T]-2"},
            {"name": "Flux Z", "symbol": "J_z", "role": "flux", "si_dimension": "[M][T]-2"},
            {"name": "Alpha Drag", "symbol": "alpha_drag", "role": "resistance", "si_dimension": "[L]2"},
        ],
        [{"source": "Quux Potential", "target": "Flux Z", "type": RelationType.PROPORTIONAL_TO, "equation": "J_z = Phi_q / alpha_drag", "assumptions": ["conservative_flux"]}],
        assumptions=["conservative_flux"]
    )
    problems.append(BenchmarkProblem(
        problem_id="E10",
        tier=ProblemTier.TIER_E,
        title="Synthetic Universe X1 Scalar Flux",
        query="In universe X1, how does Quux Potential determine Flux Z under conservative flux?",
        domains=[b_syn1],
        ground_truth_answer="Flux Z is determined by Quux Potential divided by Alpha Drag.",
        tags=["single_domain", "synthetic"]
    ))

    # =========================================================================
    # TIER I: 10 Intermediate Multi-Domain Composition Problems
    # =========================================================================
    # I01: Thermoelectric Cooler
    problems.append(BenchmarkProblem(
        problem_id="I01",
        tier=ProblemTier.TIER_I,
        title="Thermoelectric Cooling Net Heat Removal",
        query="Compose Seebeck/Peltier thermoelectric cooling with Joule dissipation and Fourier heat conduction to determine net cooling capacity.",
        domains=[b_thermal, b_seebeck],
        ground_truth_answer="Net cooling rate combines Peltier cooling (Q_p = S * T_cold * I) minus Joule back-heating (0.5 * I^2 * R) minus Fourier conductive leak (k * dT).",
        tags=["multi_domain", "composition", "thermal_electrical"]
    ))

    # I02: Electrokinetic Flow
    problems.append(BenchmarkProblem(
        problem_id="I02",
        tier=ProblemTier.TIER_I,
        title="Electro-osmotic Microfluidic Pumping",
        query="Compose electrical field electrostatic potential with fluid viscous drag to determine electro-osmotic velocity.",
        domains=[b_elec, b_fluid],
        ground_truth_answer="Electro-osmotic flow velocity balances electrostatic driving force with fluid shear viscosity: v_eo = -epsilon * zeta * E / mu.",
        tags=["multi_domain", "composition", "electrokinetics"]
    ))

    # I03: Photovoltaic-Thermal (PV/T) Degradation
    problems.append(BenchmarkProblem(
        problem_id="I03",
        tier=ProblemTier.TIER_I,
        title="Photovoltaic Electrical Efficiency under Thermal Heating",
        query="Compose solar electrical conversion with thermal accumulation to model efficiency loss as cell temperature rises.",
        domains=[b_elec, b_thermal],
        ground_truth_answer="PV efficiency decreases linearly with cell temperature: eta(T) = eta_ref * [1 - beta * (T_cell - T_ref)].",
        tags=["multi_domain", "composition", "solar_thermal"]
    ))

    # I04: Magnetohydrodynamic Pumping
    b_mag = create_bundle(
        "physics:magnetism",
        [
            {"name": "Magnetic Field", "symbol": "B_field", "role": "field", "si_dimension": "[M][T]-2[I]-1"},
            {"name": "Lorentz Body Force", "symbol": "F_lorentz", "role": "force", "si_dimension": "[M][L][T]-2"},
        ],
        [{"source": "Magnetic Field", "target": "Lorentz Body Force", "type": RelationType.PROPORTIONAL_TO, "equation": "F_lorentz = I * B_field * L"}],
    )
    problems.append(BenchmarkProblem(
        problem_id="I04",
        tier=ProblemTier.TIER_I,
        title="Magnetohydrodynamic Body Force in Conducting Fluid",
        query="Compose magnetic Lorentz force with fluid pressure gradient in a conducting channel.",
        domains=[b_fluid, b_mag],
        ground_truth_answer="Lorentz force J x B acts as a body force driving or retarding fluid flow in the momentum balance.",
        tags=["multi_domain", "composition", "MHD"]
    ))

    # I05: Electrochemical Cell
    b_chem = create_bundle(
        "chemistry:electrochemistry",
        [
            {"name": "Overpotential", "symbol": "eta_over", "role": "potential", "si_dimension": "[M][L]2[T]-3[I]-1"},
            {"name": "Reaction Current Density", "symbol": "j_rxn", "role": "flux", "si_dimension": "[I][L]-2"},
        ],
        [{"source": "Overpotential", "target": "Reaction Current Density", "type": RelationType.PROPORTIONAL_TO, "equation": "j_rxn = j_0 * eta_over"}],
    )
    problems.append(BenchmarkProblem(
        problem_id="I05",
        tier=ProblemTier.TIER_I,
        title="Electrochemical Cell Voltage Loss Composition",
        query="Compose thermodynamic Nernst potential with activation overpotential and ohmic electrolyte resistance.",
        domains=[b_elec, b_chem],
        ground_truth_answer="Operating cell voltage is E_nernst minus activation losses minus ohmic IR drop.",
        tags=["multi_domain", "composition", "battery"]
    ))

    # I06: Thermoelastic Stress
    problems.append(BenchmarkProblem(
        problem_id="I06",
        tier=ProblemTier.TIER_I,
        title="Thermoelastic Stress under Constrained Boundaries",
        query="Compose thermal expansion with elastic stress-strain in a constrained beam.",
        domains=[b_thermal, b_elasticity],
        ground_truth_answer="Constrained thermal strain creates compressive mechanical stress: sigma = -E_mod * alpha_th * dT.",
        tags=["multi_domain", "composition", "thermoelasticity"]
    ))

    # I07: Micro-Cantilever Sensor
    problems.append(BenchmarkProblem(
        problem_id="I07",
        tier=ProblemTier.TIER_I,
        title="Micro-Cantilever Resonant Frequency Mass Shift",
        query="Compose elastic stiffness and inertial mass to predict resonance frequency shift from adsorbed mass.",
        domains=[b_elasticity, b_dyn],
        ground_truth_answer="Resonant frequency omega = sqrt(k/m); added adsorbed mass delta_m shifts frequency downwards: delta_omega / omega_0 = -0.5 * delta_m / m_0.",
        tags=["multi_domain", "composition", "sensor"]
    ))

    # I08: Fluid Heat Exchanger
    problems.append(BenchmarkProblem(
        problem_id="I08",
        tier=ProblemTier.TIER_I,
        title="Heat Exchanger Thermal Rating vs Pumping Power",
        query="Compose convective heat transfer coefficient with hydraulic pressure drop pumping power.",
        domains=[b_thermal, b_fluid],
        ground_truth_answer="Higher flow rates enhance heat transfer but increase required pumping power with the cube of fluid velocity.",
        tags=["multi_domain", "composition", "heat_exchanger"]
    ))

    # I09: Piezoelectric Harvester
    b_piezo = create_bundle(
        "materials:piezoelectric",
        [
            {"name": "Piezo Electric Charge", "symbol": "Q_piezo", "role": "charge", "si_dimension": "[I][T]"},
            {"name": "Applied Strain", "symbol": "strain_s", "role": "strain", "si_dimension": "[1]"},
            {"name": "Piezoelectric Constant", "symbol": "d_coeff", "role": "coupling", "si_dimension": "[I][T][M]-1[L]-1[T]2"},
        ],
        [{"source": "Applied Strain", "target": "Piezo Electric Charge", "type": RelationType.PROPORTIONAL_TO, "equation": "Q_piezo = d_coeff * strain_s"}],
    )
    problems.append(BenchmarkProblem(
        problem_id="I09",
        tier=ProblemTier.TIER_I,
        title="Piezoelectric Vibration Energy Harvesting",
        query="Compose mechanical spring-mass vibration with piezoelectric charge generation.",
        domains=[b_elasticity, b_piezo],
        ground_truth_answer="Mechanical strain from dynamic vibration generates proportional electrical charge through piezoelectric coupling coefficient.",
        tags=["multi_domain", "composition", "piezoelectric"]
    ))

    # I10: Synthetic Multi-Field Universe X2
    b_syn2 = create_bundle(
        "synthetic:universe_x2",
        [
            {"name": "Gamma Field", "symbol": "Gamma", "role": "potential", "si_dimension": "[M][L]2[T]-2"},
            {"name": "Omega Flux", "symbol": "Omega", "role": "flux", "si_dimension": "[M][T]-2"},
        ],
        [{"source": "Gamma Field", "target": "Omega Flux", "type": RelationType.PROPORTIONAL_TO, "equation": "Omega = c_syn * Gamma"}],
    )
    problems.append(BenchmarkProblem(
        problem_id="I10",
        tier=ProblemTier.TIER_I,
        title="Synthetic Universe X2 Multi-Field Coupling",
        query="Compose synthetic Gamma Field and Quux Potential to compute total flux in universe X2.",
        domains=[b_syn1, b_syn2],
        ground_truth_answer="Total flux sums independent flux contributions across conservative potentials.",
        tags=["multi_domain", "composition", "synthetic"]
    ))

    # =========================================================================
    # TIER D: 10 Difficult Cross-Domain Transfer & Applicability Guard Problems
    # =========================================================================
    # D01: Hydraulic-Electrical Analogy (ACCEPTED / CONDITIONAL)
    problems.append(BenchmarkProblem(
        problem_id="D01",
        tier=ProblemTier.TIER_D,
        title="Hydraulic to Electrical Flow Analogy (Poiseuille -> Ohm)",
        query="Can hydraulic pipe resistance be analogously transferred to electrical resistance?",
        domains=[b_fluid, b_elec],
        source_domain_name="fluid_mechanics:pipe_flow",
        target_domain_name="physics:electromagnetism",
        ground_truth_answer="ACCEPTED: Hydraulic pressure drop to flow rate maps directly onto voltage to current.",
        expected_verdict=ApplicabilityVerdict.ACCEPTED,
        is_negative_case=False,
        tags=["cross_domain_transfer", "analogy", "fluid_electrical"]
    ))

    # D02: Thermal-Electrical Analogy (ACCEPTED / CONDITIONAL)
    b_thermal_res = create_bundle(
        "physics:thermal_network",
        [
            {"name": "Temperature Difference", "symbol": "dT_th", "role": "potential", "si_dimension": "[Θ]"},
            {"name": "Heat Current", "symbol": "Q_th", "role": "flux", "si_dimension": "[M][L]2[T]-3"},
            {"name": "Thermal Resistance", "symbol": "R_th", "role": "resistance", "si_dimension": "[M]-1[L]-2[T]3[Θ]"},
        ],
        [{"source": "Temperature Difference", "target": "Heat Current", "type": RelationType.PROPORTIONAL_TO, "equation": "dT_th = Q_th * R_th", "assumptions": ["linear", "steady_state"]}],
        assumptions=["linear", "steady_state"]
    )
    problems.append(BenchmarkProblem(
        problem_id="D02",
        tier=ProblemTier.TIER_D,
        title="Thermal to Electrical Resistance Analogy",
        query="Can Fourier thermal conduction resistance be analogously mapped onto electrical Ohm's resistance?",
        domains=[b_thermal_res, b_elec],
        source_domain_name="physics:thermal_network",
        target_domain_name="physics:electromagnetism",
        ground_truth_answer="ACCEPTED: Temperature difference (potential) and heat flow (flux) map onto voltage and current.",
        expected_verdict=ApplicabilityVerdict.ACCEPTED,
        is_negative_case=False,
        tags=["cross_domain_transfer", "analogy", "thermal_electrical"]
    ))

    # D03: Mechanical-Electrical Oscillator (ACCEPTED)
    b_mech_osc = create_bundle(
        "mechanics:damped_oscillator",
        [
            {"name": "Driving Force", "symbol": "F_drive", "role": "potential", "si_dimension": "[M][L][T]-2"},
            {"name": "Oscillator Velocity", "symbol": "v_osc", "role": "flux", "si_dimension": "[L][T]-1"},
            {"name": "Mechanical Damping", "symbol": "c_damp", "role": "resistance", "si_dimension": "[M][T]-1"},
        ],
        [{"source": "Driving Force", "target": "Oscillator Velocity", "type": RelationType.PROPORTIONAL_TO, "equation": "F_drive = v_osc * c_damp", "assumptions": ["linear"]}],
        assumptions=["linear"]
    )
    b_circuit_res = create_bundle(
        "physics:circuits",
        [
            {"name": "Electric Voltage", "symbol": "V", "role": "potential", "si_dimension": "[M][L]2[T]-3[I]-1"},
            {"name": "Electric Current", "symbol": "I", "role": "flux", "si_dimension": "[I]"},
            {"name": "Electric Resistance", "symbol": "R", "role": "resistance", "si_dimension": "[M][L]2[T]-3[I]-2"},
        ],
        [{"source": "Electric Voltage", "target": "Electric Current", "type": RelationType.PROPORTIONAL_TO, "equation": "V = I * R", "assumptions": ["linear"]}],
        assumptions=["linear"]
    )
    problems.append(BenchmarkProblem(
        problem_id="D03",
        tier=ProblemTier.TIER_D,
        title="Mechanical Damping to Electrical Resistance Analogy",
        query="Transfer mechanical viscous damping force to electrical circuit resistive drop.",
        domains=[b_mech_osc, b_circuit_res],
        source_domain_name="mechanics:damped_oscillator",
        target_domain_name="physics:circuits",
        ground_truth_answer="ACCEPTED: Driving force maps to Voltage, Velocity maps to Current, and Damping maps to Resistance.",
        expected_verdict=ApplicabilityVerdict.ACCEPTED,
        is_negative_case=False,
        tags=["cross_domain_transfer", "analogy", "mechanical_electrical"]
    ))

    # D04: Diffusion-Thermal Analogy (ACCEPTED / CONDITIONAL)
    problems.append(BenchmarkProblem(
        problem_id="D04",
        tier=ProblemTier.TIER_D,
        title="Fick's Mass Diffusion to Fourier Heat Conduction Analogy",
        query="Transfer Fick's first diffusion law to Fourier thermal conduction.",
        domains=[b_diffusion, b_thermal],
        source_domain_name="physics:mass_transport",
        target_domain_name="physics:thermodynamics",
        ground_truth_answer="ACCEPTED: Concentration gradient maps to temperature gradient, and mass diffusivity to thermal diffusivity.",
        expected_verdict=ApplicabilityVerdict.ACCEPTED,
        is_negative_case=False,
        tags=["cross_domain_transfer", "analogy", "diffusion_thermal"]
    ))

    # D05: Negative Transfer Case 1 - Quantum Tunneling to Macroscopic Pipe (REJECTED)
    b_quantum = create_bundle(
        "physics:quantum_mechanics",
        [
            {"name": "Barrier Potential", "symbol": "V_barrier", "role": "potential", "si_dimension": "[M][L]2[T]-2"},
            {"name": "Tunneling Probability", "symbol": "T_tunnel", "role": "flux", "si_dimension": "[1]"},
        ],
        [{"source": "Barrier Potential", "target": "Tunneling Probability", "type": RelationType.GOVERNED_BY, "equation": "T_tunnel = exp(-2 * k_wave * L_barrier)", "assumptions": ["wavefunction_collapse"]}],
        assumptions=["wavefunction_collapse"]
    )
    problems.append(BenchmarkProblem(
        problem_id="D05",
        tier=ProblemTier.TIER_D,
        title="Negative Transfer: Quantum Tunneling to Macroscopic Pipe Flow",
        query="Can quantum barrier tunneling be transferred to fluid flow across a closed hydraulic valve?",
        domains=[b_quantum, b_fluid],
        source_domain_name="physics:quantum_mechanics",
        target_domain_name="fluid_mechanics:pipe_flow",
        ground_truth_answer="REJECTED: Macroscopic fluid pipe flow obeys the continuum hypothesis (Navier-Stokes) with zero transmission across closed boundary; quantum wavefunction tunneling assumption is invalid.",
        expected_verdict=ApplicabilityVerdict.REJECTED,
        is_negative_case=True,
        tags=["negative_case", "applicability_guard", "quantum_fluid"]
    ))

    # D06: Negative Transfer Case 2 - Superconducting Zero Resistance to Viscous Pipe Flow (REJECTED)
    b_supercond = create_bundle(
        "physics:superconductivity",
        [
            {"name": "Cooper Pair Current", "symbol": "I_super", "role": "flux", "si_dimension": "[I]"},
            {"name": "Zero Resistance State", "symbol": "R_zero", "role": "resistance", "si_dimension": "[M][L]2[T]-3[I]-2"},
        ],
        [{"source": "Zero Resistance State", "target": "Cooper Pair Current", "type": RelationType.PROPORTIONAL_TO, "equation": "V_super = 0", "assumptions": ["macroscopic_quantum_coherence"]}],
        assumptions=["macroscopic_quantum_coherence"]
    )
    problems.append(BenchmarkProblem(
        problem_id="D06",
        tier=ProblemTier.TIER_D,
        title="Negative Transfer: Zero-Resistance Superconductivity to Normal Viscous Fluid",
        query="Can zero-resistance dissipationless flow from superconductors be transferred to room-temperature water flowing in a pipe?",
        domains=[b_supercond, b_fluid],
        source_domain_name="physics:superconductivity",
        target_domain_name="fluid_mechanics:pipe_flow",
        ground_truth_answer="REJECTED: Normal water has non-zero dynamic viscosity mu > 0 and adheres to no-slip boundary conditions, contradicting dissipationless flow.",
        expected_verdict=ApplicabilityVerdict.REJECTED,
        is_negative_case=True,
        tags=["negative_case", "applicability_guard", "superconductivity_fluid"]
    ))

    # D07: Negative Transfer Case 3 - Fourier Linear Conduction to Supersonic Shock Wave (REJECTED)
    b_shock = create_bundle(
        "aerodynamics:hypersonic",
        [
            {"name": "Shock Pressure Jump", "symbol": "P_jump", "role": "potential", "si_dimension": "[M][L]-1[T]-2"},
            {"name": "Shock Speed", "symbol": "v_shock", "role": "flux", "si_dimension": "[L][T]-1"},
        ],
        [{"source": "Shock Pressure Jump", "target": "Shock Speed", "type": RelationType.INVERSELY_PROPORTIONAL_TO}],
        assumptions=["turbulent", "non_linear", "shock_discontinuity"]
    )
    problems.append(BenchmarkProblem(
        problem_id="D07",
        tier=ProblemTier.TIER_D,
        title="Negative Transfer: Linear Fourier Conduction to Discontinuous Shock Front",
        query="Can linear Fourier heat conduction be applied across a discontinuous hypersonic shock wave?",
        domains=[b_thermal, b_shock],
        source_domain_name="physics:thermodynamics",
        target_domain_name="aerodynamics:hypersonic",
        ground_truth_answer="REJECTED: Shock fronts exhibit strong thermodynamic non-equilibrium and non-linear discontinuities, violating linear Fourier continuum conduction.",
        expected_verdict=ApplicabilityVerdict.REJECTED,
        is_negative_case=True,
        tags=["negative_case", "applicability_guard", "shock_fourier"]
    ))

    # D08: Negative Transfer Case 4 - Non-Relativistic Ohm's Law to Ultra-Relativistic Plasma (REJECTED)
    b_rel = create_bundle(
        "astrophysics:relativistic_jets",
        [
            {"name": "Relativistic Potential", "symbol": "V_rel", "role": "potential", "si_dimension": "[M][L]2[T]-3[I]-1"},
            {"name": "Relativistic Current", "symbol": "I_rel", "role": "flux", "si_dimension": "[I]"},
        ],
        [{"source": "Relativistic Current", "target": "Relativistic Potential", "type": RelationType.INVERSELY_PROPORTIONAL_TO}],
        assumptions=["relativistic", "v_near_c"]
    )
    problems.append(BenchmarkProblem(
        problem_id="D08",
        tier=ProblemTier.TIER_D,
        title="Negative Transfer: Non-Relativistic Conduction to Relativistic Jet",
        query="Can non-relativistic Ohm's law be transferred to an ultra-relativistic plasma jet where particle velocity approaches c?",
        domains=[b_elec, b_rel],
        source_domain_name="physics:electromagnetism",
        target_domain_name="astrophysics:relativistic_jets",
        ground_truth_answer="REJECTED: Relativistic speed limit v -> c causes Lorentz factor gamma -> inf and non-linear saturation, violating linear ohmic assumption and contradicting documented target behavior.",
        expected_verdict=ApplicabilityVerdict.REJECTED,
        is_negative_case=True,
        tags=["negative_case", "applicability_guard", "relativistic"]
    ))

    # D09: Synthetic Universe Transfer (ACCEPTED / CONDITIONAL)
    b_syn_target = create_bundle(
        "synthetic:universe_target",
        [
            {"name": "Synthetic Potential Target", "symbol": "Phi_tgt", "role": "potential", "si_dimension": "[M][L]2[T]-2"},
            {"name": "Synthetic Flux Target", "symbol": "J_tgt", "role": "flux", "si_dimension": "[M][T]-2"},
            {"name": "Target Impedance", "symbol": "Z_tgt", "role": "resistance", "si_dimension": "[L]2"},
        ],
        [],
        assumptions=["conservative_flux"]
    )
    problems.append(BenchmarkProblem(
        problem_id="D09",
        tier=ProblemTier.TIER_D,
        title="Synthetic Counterfactual Universe Valid Transfer",
        query="Transfer the conservative flux law from Synthetic Universe X1 to Synthetic Target Universe.",
        domains=[b_syn1, b_syn_target],
        source_domain_name="synthetic:universe_x1",
        target_domain_name="synthetic:universe_target",
        ground_truth_answer="ACCEPTED: Relational topology and dimensional structure match with conservative flux assumption preserved.",
        expected_verdict=ApplicabilityVerdict.ACCEPTED,
        is_negative_case=False,
        tags=["synthetic_counterfactual", "cross_domain_transfer"]
    ))

    # D10: Synthetic Universe Negative Case (REJECTED)
    b_syn_nonconserv = create_bundle(
        "synthetic:universe_nonconserv",
        [
            {"name": "Non-conservative Potential", "symbol": "Phi_nc", "role": "potential", "si_dimension": "[M][L]2[T]-2"},
            {"name": "Non-conservative Flux", "symbol": "J_nc", "role": "flux", "si_dimension": "[M][T]-2"},
        ],
        [{"source": "Non-conservative Potential", "target": "Non-conservative Flux", "type": RelationType.INVERSELY_PROPORTIONAL_TO}],
        assumptions=["non_conservative_flux", "dissipative_divergence"]
    )
    problems.append(BenchmarkProblem(
        problem_id="D10",
        tier=ProblemTier.TIER_D,
        title="Synthetic Counterfactual Negative Transfer Violation",
        query="Attempt transfer of conservative flux from Universe X1 into non-conservative dissipative Universe.",
        domains=[b_syn1, b_syn_nonconserv],
        source_domain_name="synthetic:universe_x1",
        target_domain_name="synthetic:universe_nonconserv",
        ground_truth_answer="REJECTED: Assumption 'conservative_flux' is incompatible with target 'non_conservative_flux', and target empirical relation contradicts transfer direction.",
        expected_verdict=ApplicabilityVerdict.REJECTED,
        is_negative_case=True,
        tags=["synthetic_counterfactual", "negative_case", "applicability_guard"]
    ))

    return problems
