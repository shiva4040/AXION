# AXION — Real-Document Secondary Evaluation Plan

**Document Version:** 2.0.0 (Audited & Verified)  
**Phase Target:** Phase 0 Evaluation Methodology  
**Scientific Discipline Focus:** Vehicle-Integrated Photovoltaics (VIPV) and Solar Electric Vehicles (SEVs)  
**Date:** November 19, 2026  

---

## 1. Objective & Scope

While synthetic benchmarks provide exact mathematical ground truth and eliminate pretraining memorization, a credible scientific AI system must also demonstrate robustness on authentic, human-written scientific literature.

This document specifies a **secondary evaluation suite** consisting of **four fully verified, open-access, peer-reviewed scientific publications** from the domain of **Vehicle-Integrated Photovoltaics (VIPV) and Solar Electric Vehicles (SEVs)**, paired with **12 manually reviewable benchmark questions** and an explicit human-in-the-loop evaluation protocol.

> **Methodological Note on Corpus Sizing:** To guarantee absolute scientific and bibliographic integrity, exactly **four tightly coupled, verified publications** are included. Rather than forcing an unrelated fifth paper merely to meet an arbitrary count (which led to mismatched citations in earlier drafts), this evaluation prioritizes thematic depth and strict factual verifiability across four deeply complementary studies spanning technological review, power electronics/MPPT, multi-physics model chains, and aerodynamic drag penalties.

---

## 2. Verified Real-World Open-Access Corpus

Every paper listed below has been independently verified through official publisher repositories (MDPI) and the Crossref registry. All four articles are published under the **Creative Commons Attribution (CC-BY 4.0)** license, permitting unrestricted academic text-and-data mining, quotation, and redistribution with attribution.

```
+--------------------------------------------------------------------------------------------------------------------------+
|                                  VERIFIED REAL-DOCUMENT EVALUATION CORPUS                                                |
+--------------------------------------------------------------------------------------------------------------------------+
| 1. "Solar-Powered Electric Vehicles: Comprehensive Review of Technology Advancements, Challenges, and Future Prospects"  |
|    - Authors: Oluwapelumi John Oluwalana, Katarzyna Grzesik                                                              |
|    - Affiliation: AGH University of Krakow, Poland                                                                       |
|    - Journal: Energies (MDPI), Vol. 18, Issue 14, Article 3650 (July 2025)                                              |
|    - DOI: 10.3390/en18143650                                                                                             |
|    - URL: https://doi.org/10.3390/en18143650                                                                             |
|    - Verification Source: Official MDPI article page and Crossref registry confirmed.                                    |
|    - License: Creative Commons Attribution (CC-BY 4.0).                                                                  |
|    - Key Focus Sections: Section 2 (Evolution of SEVs & PV Cell Architectures), Section 3 (Energy Management & Storage), |
|      Section 4 (Technical Challenges: Shading, Thermal Derating, Efficiency Envelopes).                                  |
+--------------------------------------------------------------------------------------------------------------------------+
| 2. "Feasibility Analysis and Optimisation of Vehicle-Integrated Photovoltaic (VIPV) Systems for Sustainable             |
|     Transportation"                                                                                                      |
|    - Authors: Mark Smitheram, Ehsan Gatavi                                                                               |
|    - Journal: World Electric Vehicle Journal (MDPI), Vol. 16, Issue 11, Article 610 (November 2025)                     |
|    - DOI: 10.3390/wevj16110610                                                                                           |
|    - URL: https://doi.org/10.3390/wevj16110610                                                                           |
|    - Verification Source: Official MDPI WEVJ repository and Crossref confirmed.                                          |
|    - License: Creative Commons Attribution (CC-BY 4.0).                                                                  |
|    - Key Focus Sections: Section 2 (System Architecture: Roof & Bonnet PV Layouts), Section 2.3 (MPPT Buck Converter    |
|      Dynamics), Section 3 (Fuzzy Logic Energy Distribution between Traction and Auxiliary Batteries, Daily Range Gains).|
+--------------------------------------------------------------------------------------------------------------------------+
| 3. "A Novel Model Chain for Analysing the Performance of Vehicle Integrated Photovoltaic (VIPV) Systems"                 |
|    - Authors: Hamid Samadi, Guido Ala, Miguel Centeno Brito, Marzia Traverso, Silvia Licciardi, Pietro Romano, Fabio Viola|
|    - Affiliation: University of Palermo, Italy & University of Lisbon, Portugal                                          |
|    - Journal: World Electric Vehicle Journal (MDPI), Vol. 16, Issue 11, Article 619 (November 2025)                     |
|    - DOI: 10.3390/wevj16110619                                                                                           |
|    - URL: https://doi.org/10.3390/wevj16110619                                                                           |
|    - Verification Source: Official MDPI WEVJ repository and Crossref confirmed.                                          |
|    - License: Creative Commons Attribution (CC-BY 4.0).                                                                  |
|    - Key Focus Sections: Section 2 (The VIPVLIB Model Chain: Optical, Thermal, and Electrical Sub-Models), Section 2.2   |
|      (Thermal Model: Convective Heat Loss as f(v_veh, v_wind)), Section 3 (Campus Minibus Experimental Validation).      |
+--------------------------------------------------------------------------------------------------------------------------+
| 4. "Investigation on the Aerodynamics and Energy Gain from Roof-Mounted Photovoltaic Systems for Plug-In Hybrid and     |
|     Electric Vehicles"                                                                                                   |
|    - Authors: Istvan Szabolcs Barabas, Ion Matei, Stefan Breban                                                          |
|    - Affiliation: Technical University of Cluj-Napoca, Romania                                                           |
|    - Journal: World Electric Vehicle Journal (MDPI), Vol. 17, Issue 9, Article 453 (August 2026)                          |
|    - DOI: 10.3390/wevj17090453                                                                                           |
|    - URL: https://doi.org/10.3390/wevj17090453                                                                           |
|    - Verification Source: Official MDPI WEVJ repository and Crossref confirmed.                                          |
|    - License: Creative Commons Attribution (CC-BY 4.0).                                                                  |
|    - Key Focus Sections: Section 2 (Vehicle Road Load & CFD Aerodynamic Drag Analysis), Section 3 (Drag Coefficient Cd   |
|      Penalties vs Solar Power Gains across Velocities 50-130 km/h), Section 4 (Net Energy Equilibrium Envelope).        |
+--------------------------------------------------------------------------------------------------------------------------+
```

---

## 3. Real-Document Benchmark Questions & Expected Ground Truth

The following 12 questions are directly derived from and answerable by the verified text of the four publications:

| Q ID | Target Capability | Research Question | Ground-Truth Source Anchor | Expected Evidence-Backed Answer |
| :--- | :--- | :--- | :--- | :--- |
| **REAL-01** | Extraction | *According to Oluwalana & Grzesik (Doc 1), what are the principal commercial solar cell architectures evaluated for vehicle integration, and what efficiency range is reported for monocrystalline silicon?* | Doc 1 (Oluwalana 2025), Section 2, Table 1 | Monocrystalline silicon (c-Si) remains the industry benchmark with commercial efficiencies of 20% to 24%, while multi-junction GaAs and perovskite-silicon tandems offer theoretical potential above 28% but face durability challenges. |
| **REAL-02** | Extraction | *In Smitheram & Gatavi (Doc 2), how is the VIPV array configured across vehicle surfaces, and what power conditioning topology manages the modules?* | Doc 2 (Smitheram 2025), Section 2.1 & 2.3 | Configured across roof and bonnet panels using independent DC-DC buck converters equipped with Maximum Power Point Tracking (MPPT) to handle asymmetric solar irradiance. |
| **REAL-03** | Technical Extraction | *What three distinct models comprise the VIPVLIB simulation model chain proposed by Samadi et al. (Doc 3)?* | Doc 3 (Samadi 2025), Section 2 | 1) An Optical Model (calculates dynamic solar irradiance accounting for position and curvature), 2) a Thermal Model (predicts PV cell temperature factoring in vehicle speed and wind cooling), and 3) an Electrical Model (computes I-V characteristics and net energy yield). |
| **REAL-04** | Aerodynamic Road Load | *According to Barabas et al. (Doc 4), what physical trade-off occurs when retrofitting roof-mounted PV modules onto an electric vehicle?* | Doc 4 (Barabas 2026), Section 3 & 4 | Added surface roughness and altered boundary layer profile increase aerodynamic drag coefficient ($C_d$) and frontal area, increasing mechanical road load tractive consumption, which must be offset by solar electrical generation. |
| **REAL-05** | Multi-Document Composition | *Compose the findings of Doc 2 (MPPT buck converter) and Doc 3 (Thermal Model): How does increasing vehicle speed affect net VIPV electrical generation?* | Docs 2 & 3 | Increasing vehicle speed increases forced convective cooling over the PV modules (Doc 3 Thermal Model), lowering operating temperature and mitigating thermal efficiency degradation; however, high speed increases road load tractive power demand faster than solar gain (Doc 4). |
| **REAL-06** | Energy Distribution | *In Doc 2, what control strategy is implemented to decide whether solar power charges the high-voltage traction pack or the low-voltage auxiliary battery?* | Doc 2 (Smitheram 2025), Section 3.1 | A Fuzzy Logic Controller (FLC) monitors the state of charge (SoC) of both battery packs and dynamically routes solar power to maximize overall vehicle operational efficiency. |
| **REAL-07** | Thermal Derating | *In Doc 3, how does ambient air speed and vehicle velocity influence PV module operating temperature?* | Doc 3 (Samadi 2025), Section 2.2, Eq. 4 | Relative velocity ($v_{\text{rel}} = v_{\text{veh}} + v_{\text{wind}}$) increases the convective heat transfer coefficient ($h_{\text{conv}}$), significantly lowering module equilibrium temperature compared to stationary PV installations. |
| **REAL-08** | Speed Penalty Envelope | *At high cruising speeds (e.g. 100-130 km/h in Doc 4), does a roof-mounted PV array provide a net energy surplus or a net deficit?* | Doc 4 (Barabas 2026), Section 4, Fig. 8 | At high cruising speeds (above ~90 km/h), the aerodynamic drag penalty ($\Delta F_{\text{aero}} \propto v^2$) consumes more electrical energy than the roof PV array can generate ($\sim 200\text{--}350\text{ W}$), resulting in a net energy deficit compared to a clean aerodynamic roofline. |
| **REAL-09** | Unanswerable Abstention | *What is the exact chemical stoichiometry of the organic cathode binder used in the battery cells evaluated in Doc 1?* | Doc 1 (Oluwalana 2025) | **AXION MUST ABSTAIN.** Doc 1 reviews vehicle-level PV integration and battery pack sizing trends, but contains zero data on specific cathode binder stoichiometry. |
| **REAL-10** | Unanswerable Abstention | *What is the exact numerical torsional rigidity in N*m/deg of the minibus chassis modeled in Doc 3?* | Doc 3 (Samadi 2025) | **AXION MUST ABSTAIN.** Doc 3 focuses on optical, thermal, and electrical modeling of the PV canopy; structural torsional rigidity is omitted. |
| **REAL-11** | Range Extension Evidence | *What average daily solar range extension in kilometers is reported for typical urban VIPV passenger vehicles in Doc 1 and Doc 2?* | Docs 1 & 2 | Typical urban range extension ranges from 15 km to 30 km per day under favorable sunny conditions (depending on panel area $1.5\text{--}2.2\text{ m}^2$ and vehicle electrical consumption). |
| **REAL-12** | Dispute / Caveats | *Why cannot standard stationary PV testing standards (STC: 1000 W/m^2, 25 deg C, AM 1.5) accurately predict real-world VIPV energy yields according to Doc 1 and Doc 3?* | Docs 1 & 3 | Dynamic orientation relative to the sun, transient partial shading from buildings and trees, varying vehicle speed inducing dynamic convective cooling, and non-planar 3D curved surfaces cause stationary STC ratings to misestimate VIPV output by 20% to 40%. |

---

## 4. Human Scientific Evaluation Rubric

For evaluation, generated answers from **AXION** and the **Plain RAG Baseline** are blinded (labeled System A and System B in randomized order) and scored by two independent human reviewers across five criteria (1 to 5 scale):

1. **Factual Grounding:** Every claim must be traceable to explicit sentences or tables in the cited paper.
2. **Mathematical / Physical Accuracy:** Technical terms (e.g. MPPT, $C_d$, convective cooling, SoC) must be used correctly.
3. **Boundary Condition Awareness:** Mentions key operating limits (e.g. velocity threshold for aero penalty, irradiance conditions).
4. **Citation Faithfulness:** Citations must point to exact sections/tables supporting the claim.
5. **Epistemic Modesty:** System must cleanly abstain on unanswerable questions (REAL-09, REAL-10) rather than hallucinating plausible values.
