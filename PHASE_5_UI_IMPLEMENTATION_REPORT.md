# AXION — Phase 5 UI/UX Implementation Report

**Universal Knowledge and Cross-Domain Intelligence Platform**  
**Date:** November 18, 2026  
**Status:** Completed and Verified  
**Stack:** React 19, TypeScript 5.8, Tailwind CSS v4, Three.js (WebGL), Vite 8.3, FastAPI, SQLAlchemy (Async)

---

## 1. Executive Summary

Phase 5 delivers the user-facing interface for AXION, embodying the principle:  
> **"Minimal interface, powerful intelligence, meaningful 3D visualization."**

Rather than creating a conventional admin dashboard or generic chatbot, AXION presents a modern scientific laboratory environment with an empty, focused question interface, organized multi-stage answer workspaces, and genuine interactive 3D WebGL scenes for physical explanation.

All frontend components communicate with real backend APIs across all ten AXION components, preserving epistemic tiers (`Tier 1: FACT_DOCUMENTED`, `Tier 3: HYPOTHESIS_CONJECTURED`, `Tier 4: FINDING_VALIDATED`), source provenance, and multi-domain transfer guards.

---

## 2. Design System & Visual Language

### 2.1 Color Palette
- **Main Background:** Pure White (`#FFFFFF`)
- **Secondary Surface:** Soft White (`#F8F9FB` / `#FBFBFC`)
- **Primary Text:** Dark Charcoal (`#202124`)
- **Secondary Text:** Neutral Grey (`#737780` / `#64748B`)
- **Scientific Accent:** Restrained Scientific Blue (`#2563EB`)
- **Borders & Dividers:** Very Light Grey (`#E5E7EB`)
- **Subtle Realistic Shadows:** `rgba(15, 23, 42, 0.05) 0px 4px 20px -2px`

Strictly avoided: dark themes as default, neon colors, heavy gradients, glowing borders, colorful cards, and gamified animations.

### 2.2 Typography & Spacing
- Clean modern sans-serif typography (`-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto`)
- Monospace notation (`ui-monospace, SFMono-Regular, Consolas`) for SI units, mathematical formulas, and parameters
- Generous whitespace around central inputs and readable section cards

---

## 3. Screen Implementations

### 3.1 Homepage — Empty Question Interface
- **Layout:** Strictly empty workspace. Displays exclusively:
  1. `AXION` brand wordmark with subtle `Intelligence` badge.
  2. Minimal top navigation with workspace switcher pill, history button, and `/docs` API link.
  3. One large centered question card with textarea placeholder: `"What would you like to understand or solve?"`.
  4. Paperclip document attachment button supporting `.pdf`, `.txt`, `.csv`, `.json`, and `.md` ingestion.
  5. Directional send button with auto-expansion and submit on <kbd>Enter</kbd> (<kbd>Shift</kbd>+<kbd>Enter</kbd> for newline).
- **Strict Negative Controls:** Verified zero dashboard cards, zero statistics counters, zero charts, zero sample prompts, zero welcome text, and zero decorative 3D objects on the homepage.

### 3.2 Answer Workspace — Multi-Stage Scientific Structure
Organized into structured scientific sections:
1. **Direct Answer:** 1–3 sentence immediate answer without filler.
2. **Important Points:** Key scientific principles with constitutive conservation laws and dimensional constraints.
3. **How It Works:** Procedural mechanism presented as numbered reasoning steps.
4. **Interactive 3D Explanation / Visualization:** Dedicated Three.js WebGL viewport (details below).
5. **Cross-Domain Knowledge Composition & Transfer Guard:** Structural analogical mapping table with transferred formulas ($V = m \cdot I$), applicability verdicts (`ACCEPTED`, `CONDITIONAL`, `REJECTED`), dimensional violation detection, and physical operating bounds.
6. **Final Takeaway:** Highlighted core lesson on mathematical and topological invariance.
7. **Grounding Evidence & Source Provenance:** Verified source citations, document excerpts, and epistemic tier badges.

---

## 4. 3D Scientific Visualization Engine

AXION uses genuine Three.js WebGL scenes rendered with physically realistic lighting, soft shadows, and clean lab environments:

### 4.1 Implemented Scientific Scenes
1. **Solar-Powered Electric Drivetrain (`solar_vehicle`):**
   - High-efficiency photovoltaic array (GaInP/GaAs semiconductor model)
   - MPPT buck-boost charge controller ($dP/dV = 0$)
   - LiFePO4 chemical battery pack
   - Axial-flux permanent magnet synchronous electric motor ($\tau = K_t I$)
   - Lightweight carbon-fiber monocoque chassis
   - Low-rolling-resistance wheels & hubs
   - Animated energy particle flow: Solar Panel $\to$ Controller $\to$ Battery $\to$ Motor $\to$ Wheels
2. **Electrical Conduction Circuit (`circuit`):**
   - DC voltage source, precision ceramic resistor, knife switch, copper traces, and animated charge carriers
3. **Hydraulic Hagen-Poiseuille Continuum Flow (`hydraulic`):**
   - Transparent cylindrical conduit with no-slip boundary, inlet/outlet pressure manometers ($\Delta P$), and parabolic velocity vector profile
4. **Tetrahedral Molecular Chemistry (`molecular`):**
   - $sp^3$ hybridized central core atom, covalent $\sigma$ electron pairs, and orbital angles
5. **Cross-Domain Knowledge & Transfer Topology (`cross_domain_graph`):**
   - 3D constellation linking Physics, Chemistry, Electrical, Mechanical, and Mathematics concept clusters

### 4.2 Interactive Viewport Controls
- **Orbit Controls:** Left-click drag to rotate scene, right-click drag to pan camera, scroll wheel to zoom (clamped between 3 and 40 units).
- **Raycasting Component Inspection:** Clicking any 3D component highlights the mesh and displays an overlay detailing:
  - Component name and domain
  - Physical function and mechanism
  - Governing mathematical equations (e.g., $P = \tau \omega$, $V = IR$)
  - System connections
- **Camera Presets:** Isometric (ISO), Top/Plan (TOP), Front (FRT), and Side (SIDE) views with instant camera reset.
- **Particle Flow Toggle:** Real-time pause/resume of physical flow vectors.

---

## 5. The Ten Integrated AXION Workspaces

All ten AXION workspaces operate within one unified single-page application:
1. **Ask AXION:** Primary minimal question and answer workspace.
2. **Knowledge Library:** Document ingestion (`/api/v1/sources/ingest-text`), file hash tracking (SHA256), and trust tier tagging (`PEER_REVIEWED`, `PREPRINT`, `TEXTBOOK`).
3. **Knowledge Graph Explorer:** 3D & 2D subgraph exploration (`/api/v1/graph/subgraph`) and multi-hop concept path discovery (`/api/v1/graph/paths`).
4. **Research Assistant:** Grounded prompt builder linking user inquiries to specific library documents.
5. **Reasoning Workspace:** Goal decomposition DAG visualizer (`/api/v1/reasoning/decompose`), reasoning engine runner, and literature contradiction detector.
6. **Cross-Domain Transfer:** Structural alignment evaluator comparing Structure-Mapping (SME) with Analogical Schema Projection, coupled with the multi-tiered applicability guard.
7. **Hypothesis Lab:** Synthesis of testable Tier 3 scientific hypotheses (`/api/v1/hypothesis/generate`) with falsifiability criteria.
8. **Experiment & Validation Sandbox:** Real-time sandbox test executor (`/api/v1/validation/test`) running numerical, symbolic, statistical, and ODE dynamical models.
9. **Validated Knowledge Memory:** Persistent store (`/api/v1/memory/findings`) of Tier 4 validated findings with immutable version audit logs and dependency cascade tracking.
10. **Research History:** Investigation timeline with replay capability.

---

## 6. Exact Startup and Build Commands

### Frontend Build
```powershell
cd frontend
npm install
npm run build
```
*Vite compiles the production bundle into `axion/static/` in ~235ms.*

### Backend Server Execution
```powershell
.venv\Scripts\python.exe -m uvicorn axion.api.main:app --host 127.0.0.1 --port 8000 --reload
```
*FastAPI serves both API routes under `/api/v1/` and static assets under `/` and `/assets/`.*

### Test Suite Execution
```powershell
.venv\Scripts\pytest --cov=axion --cov=benchmarks tests/
```
