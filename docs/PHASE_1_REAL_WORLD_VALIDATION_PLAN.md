# AXION — Phase 1 Real-World Scientific Document Validation Plan
## Multi-Discipline Evaluation Protocol Across Authentic Peer-Reviewed Literature

**Document Version:** 1.0.0  
**Phase Target:** Phase 1 Closure & Phase 2 Transition  
**Focus Disciplines:** Vehicle-Integrated Photovoltaics (VIPV), Aerodynamics, Power Electronics, Energy Conservation  
**Date:** November 20, 2026  
**Status:** Authoritative Real-World Validation Specification  

---

## 1. Rationale & Epistemic Boundary

While synthetic benchmarks (such as the 180-query development benchmark in Phase 1) provide exact mathematical ground truth and eliminate memorization risks, synthetic documents do not present authentic scientific noise, irregular PDF formatting, complex multi-hop terminology, or author-specific stylistic variance.

To establish genuine scientific capability without compromising the hermetic integrity of the development benchmark, this validation plan defines an **external secondary evaluation suite** based on **four verified, open-access, peer-reviewed publications** from two distinct scientific disciplines:
1. **Applied Physics & Photovoltaics** (Solid-state physics, optical modeling, semiconductor junction efficiency).
2. **Mechanical & Electrical Engineering** (CFD aerodynamic road load, DC-DC MPPT converters, battery state-of-charge routing).

---

## 2. Verified Peer-Reviewed Scientific Corpus

All four publications are licensed under Creative Commons Attribution (CC BY 4.0), permitting open text and data mining for academic evaluation:

### Publication 1: Photovoltaic Technologies & Architectural Review
- **Title:** *Solar-Powered Electric Vehicles: Comprehensive Review of Technology Advancements, Challenges, and Future Prospects*
- **Authors:** Oluwapelumi John Oluwalana, Katarzyna Grzesik (AGH University of Krakow)
- **Journal:** *Energies* (MDPI), Vol. 18, Issue 14, Article 3650 (July 2025)
- **DOI:** `10.3390/en18143650`
- **Key Sections:** Section 2 (Evolution of SEVs & PV Cell Architectures, Table 1), Section 3 (Energy Management & Storage), Section 4 (Shading, Thermal Derating).

### Publication 2: Power Conditioning & Energy Management
- **Title:** *Feasibility Analysis and Optimisation of Vehicle-Integrated Photovoltaic (VIPV) Systems for Sustainable Transportation*
- **Authors:** Mark Smitheram, Ehsan Gatavi
- **Journal:** *World Electric Vehicle Journal* (MDPI), Vol. 16, Issue 11, Article 610 (November 2025)
- **DOI:** `10.3390/wevj16110610`
- **Key Sections:** Section 2 (Roof & Bonnet Layouts), Section 2.3 (MPPT Buck Converter Dynamics), Section 3 (Fuzzy Logic Controller for Dual-Battery Energy Routing).

### Publication 3: Multi-Physics Coupled Simulation Model Chain
- **Title:** *A Novel Model Chain for Analysing the Performance of Vehicle Integrated Photovoltaic (VIPV) Systems*
- **Authors:** Hamid Samadi, Guido Ala, Miguel Centeno Brito, et al. (Univ. of Palermo & Univ. of Lisbon)
- **Journal:** *World Electric Vehicle Journal* (MDPI), Vol. 16, Issue 11, Article 619 (November 2025)
- **DOI:** `10.3390/wevj16110619`
- **Key Sections:** Section 2 (The VIPVLIB Model Chain: Optical, Thermal, and Electrical Sub-Models), Section 2.2 (Convective Heat Loss as $f(v_{\text{veh}}, v_{\text{wind}})$).

### Publication 4: Aerodynamic Drag Road Load vs. Solar Generation
- **Title:** *Investigation on the Aerodynamics and Energy Gain from Roof-Mounted Photovoltaic Systems for Plug-In Hybrid and Electric Vehicles*
- **Authors:** Istvan Szabolcs Barabas, Ion Matei, Stefan Breban (Technical Univ. of Cluj-Napoca)
- **Journal:** *World Electric Vehicle Journal* (MDPI), Vol. 17, Issue 9, Article 453 (August 2026)
- **DOI:** `10.3390/wevj17090453`
- **Key Sections:** Section 2 (CFD Aerodynamic Drag Analysis), Section 3 (Drag Coefficient $C_d$ Penalties vs Solar Power Gains, Table 3), Section 4 (Net Energy Equilibrium Envelope).

---

## 3. Real-World Diagnostic Benchmark Questions (12 Problems)

The 12 problems below require reasoning across the four authentic papers:

| Problem ID | Category | Query | Ground Truth Source | Expected Ground Truth Answer |
|---|---|---|---|---|
| **RW-01** | Extraction | *According to Oluwalana & Grzesik (Doc 1), what is the efficiency range reported for commercial monocrystalline silicon in vehicle applications?* | Doc 1, Sec. 2, Table 1 | Monocrystalline silicon (c-Si) reports commercial efficiencies between 20% and 24%. |
| **RW-02** | Extraction | *In Smitheram & Gatavi (Doc 2), what power conditioning topology manages the solar array across vehicle surfaces?* | Doc 2, Sec. 2.1 & 2.3 | Distributed DC-DC buck converters equipped with Maximum Power Point Tracking (MPPT) for roof and bonnet panels. |
| **RW-03** | Extraction | *What three sub-models constitute the VIPVLIB simulation model chain proposed by Samadi et al. (Doc 3)?* | Doc 3, Sec. 2 | 1) Optical Model, 2) Thermal Model, and 3) Electrical Model. |
| **RW-04** | Aerodynamics | *According to Barabas et al. (Doc 4), what physical trade-off occurs when retrofitting roof-mounted PV modules?* | Doc 4, Sec. 3 & 4 | Added surface roughness increases aerodynamic drag ($C_d$), increasing road load consumption that counteracts solar power generation. |
| **RW-05** | Multi-Hop Composition | *Combining Doc 2 (MPPT buck converter) and Doc 3 (Thermal Model): How does vehicle velocity influence net electrical generation efficiency?* | Docs 2 & 3 | Higher vehicle speed increases forced convective cooling, lowering module operating temperature and mitigating thermal efficiency loss. |
| **RW-06** | Energy Distribution | *In Doc 2, what control strategy determines whether solar power charges the traction pack or auxiliary battery?* | Doc 2, Sec. 3.1 | A Fuzzy Logic Controller (FLC) monitoring the state of charge (SoC) of both battery packs. |
| **RW-07** | Thermal Derating | *In Doc 3, how does relative air velocity affect PV module temperature compared to stationary PV?* | Doc 3, Sec. 2.2, Eq. 4 | Relative velocity ($v_{\text{rel}} = v_{\text{veh}} + v_{\text{wind}}$) increases the convective heat transfer coefficient ($h_{\text{conv}}$), reducing operating temperature. |
| **RW-08** | Speed Penalty Envelope | *At high cruising speeds (100–130 km/h in Doc 4), does a roof-mounted PV array produce a net energy surplus or deficit?* | Doc 4, Sec. 4, Fig. 8 | Net energy deficit: Aerodynamic drag penalty ($\Delta F_{\text{aero}} \propto v^2$) exceeds the 200–350 W generated by the roof solar panel. |
| **RW-09** | Abstention | *What is the exact chemical stoichiometry of the organic cathode binder used in the battery cells in Doc 1?* | Doc 1 | **AXION MUST ABSTAIN:** Doc 1 evaluates vehicle-level PV trends; cathode binder stoichiometry is completely unmentioned. |
| **RW-10** | Abstention | *What is the numerical torsional rigidity in N*m/deg of the minibus chassis modeled in Doc 3?* | Doc 3 | **AXION MUST ABSTAIN:** Structural torsional rigidity is omitted from Doc 3. |
| **RW-11** | Range Extension | *What typical daily solar range extension in kilometers is reported for urban VIPV in Docs 1 & 2?* | Docs 1 & 2 | Typical urban range extension is 15 km to 30 km per day under favorable sunny conditions. |
| **RW-12** | Dispute / Caveats | *Why do standard stationary PV testing conditions (STC: 1000 W/m^2, 25°C) misestimate real VIPV yields according to Docs 1 & 3?* | Docs 1 & 3 | Dynamic sun angles, transient shading, dynamic wind cooling, and curved 3D geometry cause STC ratings to misestimate output by 20% to 40%. |

---

## 4. Evaluation Rubric & Comparative Protocol

1. **Paired Blinded Comparison:** Both AXION and Plain RAG Baseline receive identical raw text from the four publications.
2. **Scoring Dimensions (1–5 scale):**
   - **Factual Grounding:** Claims must trace to explicit sentences or tables in the cited papers.
   - **Mathematical / Physical Accuracy:** Technical terms (MPPT, $C_d$, convective cooling, SoC) must be used correctly.
   - **Boundary Condition Awareness:** Mentions key operating limits (e.g. speed threshold for aero penalty).
   - **Citation Faithfulness:** Citations must point to exact sections or tables.
   - **Epistemic Modesty:** System must cleanly abstain on unanswerable questions (RW-09, RW-10) rather than hallucinating plausible values.
