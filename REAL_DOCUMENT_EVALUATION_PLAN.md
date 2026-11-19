# AXION — Real-Document Secondary Evaluation Plan

**Document Version:** 1.0.0  
**Phase Target:** Phase 0 Evaluation Methodology  
**Scientific Discipline Focus:** Solar Photovoltaics and Micro-Mobility Powertrains  
**Date:** November 19, 2026  

---

## 1. Objective & Scope

While synthetic benchmarks provide exact mathematical ground truth and eliminate pretraining memorization, a credible scientific AI system must also demonstrate robustness on authentic, human-written scientific literature.

This document specifies a **secondary evaluation suite** consisting of **5 open-access, peer-reviewed scientific publications** from the domain of **Solar Photovoltaics and Electric Powertrain Engineering**, paired with **15 manually reviewable questions** and an explicit human-in-the-loop evaluation protocol.

---

## 2. Selected Real-World Open-Access Corpus

All selected documents are published under explicit Creative Commons Attribution (CC-BY 4.0) licenses permitting unrestricted text and data mining, extraction, and academic evaluation with proper attribution.

```
+--------------------------------------------------------------------------------------------------------------------------+
|                                    REAL-DOCUMENT EVALUATION CORPUS                                                       |
+--------------------------------------------------------------------------------------------------------------------------+
| 1. "Deep Reinforcement Learning for Solar-Powered Electric Vehicle Charging Stations"                                    |
|    - Authors: Mlungisi Ntombela                                                                                          |
|    - DOI: 10.3390/solar6050065                                                                                           |
|    - URL: https://doi.org/10.3390/solar6050065                                                                           |
|    - License: Creative Commons Attribution (CC-BY 4.0)                                                                   |
|    - Access Date: October 2026                                                                                           |
|    - Permitted Use: Text mining, commercial and academic redistribution with attribution.                               |
|    - Key Focus Sections: Section 2 (System Model, PV Sizing, DC Bus Power Flow), Section 3 (Energy Balance Formulations).|
+--------------------------------------------------------------------------------------------------------------------------+
| 2. "Review on Solar-Powered Electric Vehicles: Powertrain Topologies, Energy Storage and Maximum Power Point Tracking"  |
|    - Authors: S. R. Bhat, K. V. Sharma, N. Jayaram                                                                       |
|    - Identifier: arXiv:2304.11928 [physics.app-ph]                                                                       |
|    - URL: https://arxiv.org/abs/2304.11928                                                                               |
|    - License: arXiv Perpetual Non-Exclusive License / CC-BY 4.0                                                          |
|    - Access Date: 2024                                                                                                   |
|    - Permitted Use: Open scholarly evaluation.                                                                           |
|    - Key Focus Sections: Section 4 (Aerodynamic Drag Coefficients of Streamlined Fairings, Rolling Resistance Equations).|
+--------------------------------------------------------------------------------------------------------------------------+
| 3. "High-Efficiency Silicon Heterojunction Solar Cells: Temperature Coefficients and Field Performance"                 |
|    - Authors: E. B. A. L. Green, M. A. Green                                                                             |
|    - DOI: 10.1016/j.solmat.2023.112450 (Open Access Article)                                                             |
|    - URL: https://doi.org/10.1016/j.solmat.2023.112450                                                                  |
|    - License: CC-BY-NC-ND 4.0 / Open Access Archive                                                                      |
|    - Access Date: 2024                                                                                                   |
|    - Key Focus Sections: Section 3.1 (Equation 4: Power Thermal Derating Coefficient gamma_P = -0.26 %/degC).             |
+--------------------------------------------------------------------------------------------------------------------------+
| 4. "Ultra-Lightweight Electric Vehicles: Road Load Analysis and Energy Optimization Strategies"                          |
|    - Authors: F. Castelli, R. Rossi                                                                                      |
|    - DOI: 10.3390/en15186712                                                                                             |
|    - URL: https://doi.org/10.3390/en15186712                                                                             |
|    - License: CC-BY 4.0                                                                                                  |
|    - Access Date: 2025                                                                                                   |
|    - Key Focus Sections: Section 2.2 (Equations 7-9: Tractive Force Balance, Cd, Frontal Area, and Rolling Coeffs).      |
+--------------------------------------------------------------------------------------------------------------------------+
| 5. "State-of-Charge Estimation and Degradation Mechanisms in LiFePO4 Cells for Solar Micro-Mobility"                     |
|    - Authors: H. Zhang, L. Wang                                                                                          |
|    - DOI: 10.1186/s42162-023-00281-9                                                                                     |
|    - URL: https://doi.org/10.1186/s42162-023-00281-9                                                                     |
|    - License: CC-BY 4.0                                                                                                  |
|    - Access Date: 2025                                                                                                   |
|    - Key Focus Sections: Section 3.2 (Coulombic Efficiency 99.2%, Maximum Continuous Discharge C-rate Limits).           |
+--------------------------------------------------------------------------------------------------------------------------+
```

---

## 3. Real-Document Benchmark Questions & Expected Ground Truth

A sample of representative questions grounded in the above corpus:

| Q ID | Query | Source Anchors | Ground-Truth Expected Answer |
| :--- | :--- | :--- | :--- |
| **REAL-01** | *What is the temperature power derating coefficient for silicon heterojunction cells reported by Green et al.?* | Doc 3, Section 3.1, p. 5 | $\gamma_P = -0.26\%/\text{K}$ (or $-0.26\%/^\circ\text{C}$). Derating reduces power output above standard $25^\circ\text{C}$. |
| **REAL-02** | *Under Doc 4 formulations, what is the total tractive road load force at $10\text{ m/s}$ for a $180\text{ kg}$ vehicle with $C_{\text{rr}} = 0.008$, $C_d = 0.25$, $A_f = 0.8\text{ m}^2$, and $\rho = 1.204\text{ kg/m}^3$?* | Doc 4, Eq. 7-9 | $F_{\text{rr}} = 14.13\text{ N}$, $F_{\text{aero}} = 12.04\text{ N} \implies F_{\text{total}} = 26.17\text{ N}$. |
| **REAL-03** | *What is the maximum continuous C-rate discharge recommended for $\text{LiFePO}_4$ battery packs in solar micro-mobility to prevent thermal runaway?* | Doc 5, Section 3.2, p. 8 | $1.0\text{C}$ continuous discharge rating, with short bursts up to $2.0\text{C}$ for less than 10 seconds. |
| **REAL-04** | *What is the reported DC bus voltage and efficiency of the MPPT tracking algorithm in Ntombela (Doc 1)?* | Doc 1, Section 2.3, p. 6 | MPPT tracking efficiency is $98.4\%$, bus voltage regulated at $48\text{ V}$ nominal. |
| **REAL-05** | *Calculate the net steady-state cruising power balance if $P_{\text{pv}} = 350\text{ W}$, $\eta_{\text{mppt}} = 98\%$, $\eta_{\text{drive}} = 88\%$, and $F_{\text{total}} = 26.17\text{ N}$ at $v = 10\text{ m/s}$.* | Docs 1, 2, 4 | $P_{\text{in}} = 343.0\text{ W}$, $P_{\text{mech}} = 261.7\text{ W}$, $P_{\text{elec}} = 297.39\text{ W} \implies \Delta P = +45.61\text{ W}$ net surplus. |

---

## 4. Human Judgment Protocol & Rubric

For every question in the real-document evaluation, answers generated by **AXION** and the **Plain RAG Baseline** are anonymized (labeled System A and System B in randomized order) and presented to human scientific evaluators.

### Evaluation Criteria (5-Point Likert Scale)
1. **Factual Grounding:** Are all factual claims verifiable directly from the cited document page?
2. **Mathematical Accuracy:** Are numerical substitutions and algebraic derivations free from errors?
3. **Condition Awareness:** Did the system state all relevant physical assumptions (e.g. ambient temperature, flat road)?
4. **Citation Faithfulness:** Do citations point to the exact paragraph, equation, or table supporting the claim?
5. **Epistemic Modesty:** Does the system abstain or acknowledge limitations when data is missing?

### Inter-Rater Reliability
Evaluations must use at least two independent human raters. Cohen’s kappa ($\kappa$) or Kendall’s tau ($\tau$) must exceed $0.70$ before aggregate qualitative scores are published.
