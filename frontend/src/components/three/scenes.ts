import * as THREE from 'three';

export interface ComponentMetadata {
  id: string;
  name: string;
  domain: string;
  functionDesc: string;
  equations: string[];
  connections: string[];
  energyFlowOrder?: number;
}

export interface SceneModelData {
  title: string;
  description: string;
  group: THREE.Group;
  components: Record<string, ComponentMetadata>;
  updateParticles?: (delta: number) => void;
}

export function buildElectricMotorScene(): SceneModelData {
  const group = new THREE.Group();
  const components: Record<string, ComponentMetadata> = {};

  // 1. Stator Casing & Structural Housing
  const statorGeo = new THREE.CylinderGeometry(2.4, 2.4, 3.2, 32, 1, true);
  const statorMat = new THREE.MeshStandardMaterial({
    color: 0x64748b,
    metalness: 0.7,
    roughness: 0.3,
    side: THREE.DoubleSide,
    transparent: true,
    opacity: 0.5,
  });
  const stator = new THREE.Mesh(statorGeo, statorMat);
  stator.rotation.x = Math.PI / 2;
  stator.position.set(0, 1.6, 0);
  stator.name = 'stator';
  group.add(stator);

  components['stator'] = {
    id: 'stator',
    name: 'Stator Magnetic Frame',
    domain: 'Electrodynamics & Structural Mechanics',
    functionDesc: 'The stationary outer frame that houses the permanent magnets or field windings, providing an enclosed low-reluctance magnetic flux path and mechanical containment.',
    equations: ['\\oint \\vec{H} \\cdot d\\vec{l} = N I', '\\nabla \\cdot \\vec{B} = 0'],
    connections: ['magnets', 'bearings'],
  };

  // 2. Permanent Magnetic Poles (North & South)
  const magGeo = new THREE.BoxGeometry(0.5, 1.4, 2.8);
  const northMat = new THREE.MeshStandardMaterial({ color: 0xdc2626, metalness: 0.5, roughness: 0.3 }); // Red North
  const southMat = new THREE.MeshStandardMaterial({ color: 0x2563eb, metalness: 0.5, roughness: 0.3 }); // Blue South

  const northPole = new THREE.Mesh(magGeo, northMat);
  northPole.position.set(-1.8, 1.6, 0);
  northPole.name = 'magnets';
  group.add(northPole);

  const southPole = new THREE.Mesh(magGeo, southMat);
  southPole.position.set(1.8, 1.6, 0);
  southPole.name = 'magnets';
  group.add(southPole);

  components['magnets'] = {
    id: 'magnets',
    name: 'Permanent Stator Magnets (North & South Poles)',
    domain: 'Magnetostatics & Materials Physics',
    functionDesc: 'Generates a strong, uniform transverse magnetic field (B-field) crossing the air gap between stator and rotor.',
    equations: ['\\vec{B} = \\mu_0 (\\vec{H} + \\vec{M})', '\\Phi = \\iint \\vec{B} \\cdot d\\vec{A}'],
    connections: ['stator', 'rotor'],
  };

  // 3. Rotating Assembly Group (Rotor + Shaft + Coils + Commutator)
  const rotorGroup = new THREE.Group();
  rotorGroup.position.set(0, 1.6, 0);
  rotorGroup.rotation.x = Math.PI / 2;
  group.add(rotorGroup);

  // Central Drive Shaft
  const shaftGeo = new THREE.CylinderGeometry(0.18, 0.18, 4.4, 24);
  const shaftMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.85, roughness: 0.15 });
  const shaft = new THREE.Mesh(shaftGeo, shaftMat);
  shaft.name = 'shaft';
  rotorGroup.add(shaft);

  components['shaft'] = {
    id: 'shaft',
    name: 'Hardened Steel Drive Shaft',
    domain: 'Mechanical Engineering & Machine Design',
    functionDesc: 'Transfers the generated electromagnetic rotational torque directly to external mechanical loads.',
    equations: ['P = \\tau \\cdot \\omega', '\\tau_{max} = \\frac{\\pi d^3}{16} \\tau_{shear}'],
    connections: ['rotor', 'external_load'],
  };

  // Rotor Core (Laminated Armature)
  const rotorGeo = new THREE.CylinderGeometry(1.2, 1.2, 2.2, 24);
  const rotorMat = new THREE.MeshStandardMaterial({ color: 0x475569, metalness: 0.6, roughness: 0.4 });
  const rotor = new THREE.Mesh(rotorGeo, rotorMat);
  rotor.name = 'rotor';
  rotorGroup.add(rotor);

  components['rotor'] = {
    id: 'rotor',
    name: 'Laminated Armature Rotor',
    domain: 'Electromagnetic Machines',
    functionDesc: 'The rotating cylindrical assembly of laminated silicon steel sheets that channels magnetic flux and supports the copper windings.',
    equations: ['\\tau = r \\times \\vec{F}', 'I_{moment} = \\frac{1}{2} M R^2'],
    connections: ['shaft', 'coils', 'commutator'],
  };

  // Copper Windings / Electromagnetic Coils
  const coilMat = new THREE.MeshStandardMaterial({ color: 0xb45309, metalness: 0.8, roughness: 0.2 });
  const coil1 = new THREE.Mesh(new THREE.BoxGeometry(0.35, 2.3, 0.6), coilMat);
  coil1.position.set(0, 0, 0.9);
  coil1.name = 'coils';
  rotorGroup.add(coil1);

  const coil2 = new THREE.Mesh(new THREE.BoxGeometry(0.35, 2.3, 0.6), coilMat);
  coil2.position.set(0, 0, -0.9);
  coil2.name = 'coils';
  rotorGroup.add(coil2);

  const coil3 = new THREE.Mesh(new THREE.BoxGeometry(0.6, 2.3, 0.35), coilMat);
  coil3.position.set(0.9, 0, 0);
  coil3.name = 'coils';
  rotorGroup.add(coil3);

  const coil4 = new THREE.Mesh(new THREE.BoxGeometry(0.6, 2.3, 0.35), coilMat);
  coil4.position.set(-0.9, 0, 0);
  coil4.name = 'coils';
  rotorGroup.add(coil4);

  components['coils'] = {
    id: 'coils',
    name: 'Electromagnetic Armature Coils (Copper Windings)',
    domain: 'Electrodynamics & Ampère-Lorentz Physics',
    functionDesc: 'Carries electric current through the magnetic field, producing Lorentz forces perpendicular to both current and magnetic flux: F = I (L × B).',
    equations: ['\\vec{F} = I (\\vec{L} \\times \\vec{B})', '\\tau = N I A B \\sin(\\theta)'],
    connections: ['rotor', 'commutator'],
  };

  // Commutator & Carbon Brushes
  const commGeo = new THREE.CylinderGeometry(0.45, 0.45, 0.5, 16);
  const commMat = new THREE.MeshStandardMaterial({ color: 0xd97706, metalness: 0.7, roughness: 0.2 });
  const commutator = new THREE.Mesh(commGeo, commMat);
  commutator.position.set(0, 1.6, 0);
  commutator.name = 'commutator';
  rotorGroup.add(commutator);

  components['commutator'] = {
    id: 'commutator',
    name: 'Split-Ring Commutator & Carbon Brushes',
    domain: 'Electrical Machines & Switching Theory',
    functionDesc: 'A mechanical rotary switch that reverses the direction of electric current in the rotor coils every 180 degrees, ensuring rotational torque remains unidirectional.',
    equations: ['\\tau_{avg} = \\frac{2}{\\pi} \\tau_{peak}', 'f_{comm} = \\frac{p \\cdot n}{120}'],
    connections: ['coils', 'external_power'],
  };

  // Magnetic Field Lines (Flux Arrows / Particles)
  const fluxCount = 24;
  const fluxGeo = new THREE.BufferGeometry();
  const fluxPos = new Float32Array(fluxCount * 3);
  for (let i = 0; i < fluxCount; i++) {
    fluxPos[i * 3] = -1.5 + (i % 6) * 0.6;
    fluxPos[i * 3 + 1] = 1.0 + Math.floor(i / 6) * 0.4;
    fluxPos[i * 3 + 2] = (Math.random() - 0.5) * 1.8;
  }
  fluxGeo.setAttribute('position', new THREE.BufferAttribute(fluxPos, 3));
  const fluxMat = new THREE.PointsMaterial({ color: 0x38bdf8, size: 0.12, transparent: true, opacity: 0.8 });
  const fluxParticles = new THREE.Points(fluxGeo, fluxMat);
  group.add(fluxParticles);

  // Dynamic Animation: Rotor Rotation & Magnetic Flux Oscillation
  const updateParticles = (delta: number) => {
    rotorGroup.rotation.y += delta * 2.5; // Smooth mechanical shaft rotation
    const posAttr = fluxGeo.attributes.position as THREE.BufferAttribute;
    for (let i = 0; i < fluxCount; i++) {
      let x = posAttr.getX(i);
      x += delta * 1.5;
      if (x > 1.6) x = -1.6;
      posAttr.setX(i, x);
    }
    posAttr.needsUpdate = true;
  };

  return {
    title: 'DC Electric Motor Electromagnetic Core',
    description: 'Electromechanical energy conversion: Electric current through rotor coils interacts with stator magnetic flux to generate continuous rotational torque via Lorentz forces.',
    group,
    components,
    updateParticles,
  };
}

export function buildPhotosynthesisScene(): SceneModelData {
  const group = new THREE.Group();
  const components: Record<string, ComponentMetadata> = {};

  // 1. Chloroplast Double Membrane Envelope
  const envelopeGeo = new THREE.SphereGeometry(3.2, 32, 24);
  envelopeGeo.scale(1.4, 0.7, 1.0);
  const envelopeMat = new THREE.MeshPhysicalMaterial({
    color: 0x10b981,
    transparent: true,
    opacity: 0.22,
    roughness: 0.2,
    transmission: 0.8,
    side: THREE.DoubleSide,
  });
  const envelope = new THREE.Mesh(envelopeGeo, envelopeMat);
  envelope.position.set(0, 1.8, 0);
  envelope.name = 'envelope';
  group.add(envelope);

  components['envelope'] = {
    id: 'envelope',
    name: 'Chloroplast Double-Membrane Envelope',
    domain: 'Cellular Biochemistry & Membrane Biophysics',
    functionDesc: 'Selectively permeable lipid bilayer regulating metabolite transport (CO2, triose phosphates, ATP) between the cytosol and stroma.',
    equations: ['J = -P (C_{in} - C_{out})', '\\Delta G = \\Delta H - T \\Delta S'],
    connections: ['stroma'],
  };

  // 2. Thylakoid Grana (Stacked Membrane Discs)
  const discGeo = new THREE.CylinderGeometry(0.8, 0.8, 0.14, 24);
  const thylakoidMat = new THREE.MeshStandardMaterial({ color: 0x047857, roughness: 0.4 });

  const granaStacks = [
    [-1.6, 0],
    [-0.5, 0.8],
    [0.6, -0.6],
    [1.8, 0.4],
  ];

  granaStacks.forEach(([gx, gz], sIdx) => {
    for (let i = 0; i < 5; i++) {
      const disc = new THREE.Mesh(discGeo, thylakoidMat);
      disc.position.set(gx, 1.2 + i * 0.22, gz);
      disc.name = 'thylakoids';
      group.add(disc);
    }
  });

  components['thylakoids'] = {
    id: 'thylakoids',
    name: 'Thylakoid Membrane Grana (Light-Dependent Site)',
    domain: 'Biophysics & Photochemistry',
    functionDesc: 'Folded membrane stacks containing chlorophyll pigment complexes where solar photon energy is harnessed to drive water photolysis and generate a proton gradient.',
    equations: ['2\\text{H}_2\\text{O} + 4h\\nu \\longrightarrow \\text{O}_2 + 4\\text{H}^+ + 4e^-', '\\Delta p = \\Delta \\psi - 59 \\Delta \\text{pH}'],
    connections: ['photosystems', 'atp_synthase'],
  };

  // 3. Reaction Centers (Photosystems I and II)
  const psGeo = new THREE.BoxGeometry(0.4, 0.3, 0.4);
  const psMat = new THREE.MeshStandardMaterial({ color: 0xfacc15, metalness: 0.6, roughness: 0.2 });
  const ps1 = new THREE.Mesh(psGeo, psMat);
  ps1.position.set(-1.6, 2.35, 0);
  ps1.name = 'photosystems';
  group.add(ps1);

  const ps2 = new THREE.Mesh(psGeo, psMat);
  ps2.position.set(1.8, 2.35, 0.4);
  ps2.name = 'photosystems';
  group.add(ps2);

  components['photosystems'] = {
    id: 'photosystems',
    name: 'Photosystems II & I Reaction Centers (P680 & P700)',
    domain: 'Quantum Biology & Resonance Energy Transfer',
    functionDesc: 'Specialized chlorophyll a dimers that undergo charge separation upon photon absorption, transferring excited electrons to plastoquinone.',
    equations: ['E_{photon} = h \\nu = \\frac{hc}{\\lambda}', 'k_{FRET} = \\frac{1}{\\tau_D} \\left(\\frac{R_0}{r}\\right)^6'],
    connections: ['thylakoids', 'stroma'],
  };

  // 4. ATP Synthase Molecular Complex
  const atpGeo = new THREE.CylinderGeometry(0.3, 0.35, 0.6, 16);
  const atpMat = new THREE.MeshStandardMaterial({ color: 0x3b82f6, metalness: 0.4, roughness: 0.3 });
  const atpSynthase = new THREE.Mesh(atpGeo, atpMat);
  atpSynthase.position.set(0.6, 2.45, -0.6);
  atpSynthase.name = 'atp_synthase';
  group.add(atpSynthase);

  components['atp_synthase'] = {
    id: 'atp_synthase',
    name: 'CF₀-CF₁ ATP Synthase Rotary Motor',
    domain: 'Bioenergetics & Chemiosmosis',
    functionDesc: 'Utilizes the high proton motive force across the thylakoid membrane to rotate catalytic subunits and synthesize ATP from ADP and Pi.',
    equations: ['\\text{ADP} + \\text{P}_i + 3\\text{H}^+_{lumen} \\rightleftharpoons \\text{ATP} + \\text{H}_2\\text{O} + 3\\text{H}^+_{stroma}'],
    connections: ['thylakoids', 'stroma'],
  };

  // 5. Stroma & Calvin Cycle Fluid
  components['stroma'] = {
    id: 'stroma',
    name: 'Aqueous Stroma (Calvin Cycle / Carbon Fixation)',
    domain: 'Enzymology & Organic Chemistry',
    functionDesc: 'The protein-rich fluid surrounding thylakoids where the enzyme RuBisCO fixes atmospheric CO2 into 3-phosphoglycerate and synthesizes glucose.',
    equations: ['\\text{RuBP} + \\text{CO}_2 + \\text{H}_2\\text{O} \\xrightarrow{\\text{RuBisCO}} 2 (3\\text{-PGA})', '6\\text{CO}_2 + 18\\text{ATP} + 12\\text{NADPH} \\to \\text{C}_6\\text{H}_{12}\\text{O}_6'],
    connections: ['thylakoids', 'envelope'],
  };

  // Incoming Solar Photons (Animated Light Packets)
  const photonCount = 36;
  const photonGeo = new THREE.BufferGeometry();
  const photonPos = new Float32Array(photonCount * 3);
  for (let i = 0; i < photonCount; i++) {
    photonPos[i * 3] = (Math.random() - 0.5) * 4;
    photonPos[i * 3 + 1] = 4 + Math.random() * 2;
    photonPos[i * 3 + 2] = (Math.random() - 0.5) * 3;
  }
  photonGeo.setAttribute('position', new THREE.BufferAttribute(photonPos, 3));
  const photonMat = new THREE.PointsMaterial({ color: 0xfef08a, size: 0.16, transparent: true, opacity: 0.9 });
  const photons = new THREE.Points(photonGeo, photonMat);
  group.add(photons);

  const updateParticles = (delta: number) => {
    const attr = photonGeo.attributes.position as THREE.BufferAttribute;
    for (let i = 0; i < photonCount; i++) {
      let y = attr.getY(i) - delta * 3.0;
      if (y < 1.0) y = 5.5 + Math.random();
      attr.setY(i, y);
    }
    attr.needsUpdate = true;
  };

  return {
    title: 'Chloroplast Photochemical & Calvin Cycle System',
    description: 'Biochemical energy conversion: Solar photons excite chlorophyll electrons in thylakoid membranes, generating ATP and NADPH to fix atmospheric CO₂ into carbohydrates.',
    group,
    components,
    updateParticles,
  };
}

export function buildHydraulicLiftScene(): SceneModelData {
  const group = new THREE.Group();
  const components: Record<string, ComponentMetadata> = {};

  // 1. Narrow Input Cylinder (Area A₁)
  const inCylGeo = new THREE.CylinderGeometry(0.4, 0.4, 2.5, 24, 1, true);
  const cylMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.6, roughness: 0.3, transparent: true, opacity: 0.7 });
  const inCyl = new THREE.Mesh(inCylGeo, cylMat);
  inCyl.position.set(-2.5, 1.25, 0);
  inCyl.name = 'input_piston';
  group.add(inCyl);

  // Narrow Input Piston Head
  const inPistGeo = new THREE.CylinderGeometry(0.38, 0.38, 0.5, 24);
  const pistMat = new THREE.MeshStandardMaterial({ color: 0xd97706, metalness: 0.8, roughness: 0.2 });
  const inPiston = new THREE.Mesh(inPistGeo, pistMat);
  inPiston.position.set(-2.5, 1.6, 0);
  inPiston.name = 'input_piston';
  group.add(inPiston);

  components['input_piston'] = {
    id: 'input_piston',
    name: 'Input Piston (Small Area A₁)',
    domain: 'Hydrostatics & Fluid Mechanics',
    functionDesc: 'A small-area piston where a modest external input force F₁ is applied, creating a uniform hydrostatic fluid pressure P = F₁ / A₁.',
    equations: ['P = \\frac{F_1}{A_1}', 'A_1 = \\pi r_1^2'],
    connections: ['hydraulic_fluid', 'output_cylinder'],
  };

  // 2. Wide Output Cylinder (Area A₂)
  const outCylGeo = new THREE.CylinderGeometry(1.4, 1.4, 2.5, 28, 1, true);
  const outCyl = new THREE.Mesh(outCylGeo, cylMat);
  outCyl.position.set(1.8, 1.25, 0);
  outCyl.name = 'output_cylinder';
  group.add(outCyl);

  // Wide Output Piston Head
  const outPistGeo = new THREE.CylinderGeometry(1.38, 1.38, 0.5, 28);
  const outPiston = new THREE.Mesh(outPistGeo, pistMat);
  outPiston.position.set(1.8, 1.4, 0);
  outPiston.name = 'output_cylinder';
  group.add(outPiston);

  components['output_cylinder'] = {
    id: 'output_cylinder',
    name: 'Output Cylinder & Ram (Large Area A₂)',
    domain: 'Fluid Power & Mechanical Systems',
    functionDesc: 'A large-area cylinder that receives the transmitted hydrostatic pressure and produces an amplified lifting force: F₂ = P × A₂ = F₁ (A₂ / A₁).',
    equations: ['F_2 = P \\cdot A_2 = F_1 \\left(\\frac{A_2}{A_1}\\right)', '\\text{Mechanical Advantage} = \\frac{A_2}{A_1} = \\left(\\frac{r_2}{r_1}\\right)^2'],
    connections: ['hydraulic_fluid', 'lift_platform'],
  };

  // 3. Fluid Manifold / Connecting Base
  const baseManifoldGeo = new THREE.BoxGeometry(5.2, 0.4, 1.2);
  const manifoldMat = new THREE.MeshStandardMaterial({ color: 0x64748b, metalness: 0.5, roughness: 0.4 });
  const manifold = new THREE.Mesh(baseManifoldGeo, manifoldMat);
  manifold.position.set(-0.35, 0.2, 0);
  group.add(manifold);

  // 4. Incompressible Hydraulic Fluid (Visualized inside manifold & cylinders)
  const fluidMat = new THREE.MeshPhysicalMaterial({
    color: 0x0284c7,
    transmission: 0.7,
    transparent: true,
    opacity: 0.85,
    roughness: 0.1,
  });
  const fluidBody = new THREE.Mesh(new THREE.BoxGeometry(5.0, 0.32, 0.9), fluidMat);
  fluidBody.position.set(-0.35, 0.2, 0);
  fluidBody.name = 'hydraulic_fluid';
  group.add(fluidBody);

  components['hydraulic_fluid'] = {
    id: 'hydraulic_fluid',
    name: 'Incompressible Hydraulic Fluid (Pascal’s Medium)',
    domain: 'Continuum Mechanics & Pascal’s Principle',
    functionDesc: 'An incompressible fluid transmits applied hydrostatic pressure undiminished and instantaneously to every portion of the fluid and cylinder walls.',
    equations: ['P_1 = P_2 = \\text{constant}', '\\beta = -V \\frac{dP}{dV} \\to \\infty \\quad (\\text{incompressible})'],
    connections: ['input_piston', 'output_cylinder'],
  };

  // 5. Heavy-Duty Lift Platform
  const platGeo = new THREE.BoxGeometry(3.6, 0.2, 2.2);
  const platMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, metalness: 0.7, roughness: 0.3 });
  const platform = new THREE.Mesh(platGeo, platMat);
  platform.position.set(1.8, 1.75, 0);
  platform.name = 'lift_platform';
  group.add(platform);

  components['lift_platform'] = {
    id: 'lift_platform',
    name: 'Structural Load Platform',
    domain: 'Statics & Structural Equilibrium',
    functionDesc: 'Supports heavy external payload (e.g., motor vehicle or industrial equipment) elevated by the output ram.',
    equations: ['W = F_1 \\cdot d_1 = F_2 \\cdot d_2', 'd_2 = d_1 \\left(\\frac{A_1}{A_2}\\right)'],
    connections: ['output_cylinder'],
  };

  // Dynamic Piston Displacement Animation
  let oscTime = 0;
  const updateParticles = (delta: number) => {
    oscTime += delta * 1.5;
    const disp = Math.sin(oscTime) * 0.25;
    inPiston.position.y = 1.6 - disp;
    // Area ratio approx 1 : 12, so displacement ratio is 12 : 1
    outPiston.position.y = 1.4 + disp * (0.4 / 1.4) ** 2;
    platform.position.y = 1.75 + disp * (0.4 / 1.4) ** 2;
  };

  return {
    title: 'Hydraulic Lift Force-Multiplier System',
    description: 'Pascal’s Principle in action: Hydrostatic pressure transmitted through incompressible fluid creates proportional force amplification: F₂ = F₁ (A₂ / A₁).',
    group,
    components,
    updateParticles,
  };
}

export function buildSolarVehicleScene(): SceneModelData {
  const group = new THREE.Group();
  const components: Record<string, ComponentMetadata> = {};

  // 1. Lightweight Chassis / Mechanical Frame
  const chassisGeo = new THREE.BoxGeometry(6, 0.4, 2.6);
  const chassisMat = new THREE.MeshStandardMaterial({
    color: 0xe2e8f0,
    metalness: 0.6,
    roughness: 0.3,
  });
  const chassis = new THREE.Mesh(chassisGeo, chassisMat);
  chassis.position.set(0, 0.6, 0);
  chassis.name = 'chassis';
  chassis.castShadow = true;
  chassis.receiveShadow = true;
  group.add(chassis);
  components['chassis'] = {
    id: 'chassis',
    name: 'Carbon-Fiber Monocoque Chassis',
    domain: 'Mechanical Engineering & Materials Science',
    functionDesc: 'Provides structural rigidity, torsional stiffness, and aerodynamic shielding while minimizing vehicle curb weight.',
    equations: ['\\sigma = \\frac{M y}{I}', 'F_{drag} = \\frac{1}{2} \\rho v^2 C_d A'],
    connections: ['wheels', 'solar_panel', 'battery'],
  };

  // 2. High-Efficiency Solar Panel Array
  const panelGeo = new THREE.BoxGeometry(4.8, 0.1, 2.2);
  const panelMat = new THREE.MeshStandardMaterial({
    color: 0x1e293b,
    roughness: 0.2,
    metalness: 0.8,
  });
  const panel = new THREE.Mesh(panelGeo, panelMat);
  panel.position.set(0, 1.4, 0);
  panel.name = 'solar_panel';
  panel.castShadow = true;
  group.add(panel);

  const gridHelper = new THREE.GridHelper(4.6, 12, 0x38bdf8, 0x1e3a8a);
  gridHelper.position.set(0, 1.46, 0);
  gridHelper.scale.set(1, 1, 0.45);
  group.add(gridHelper);

  components['solar_panel'] = {
    id: 'solar_panel',
    name: 'Photovoltaic Solar Array (GaInP/GaAs)',
    domain: 'Physics & Semiconductor Electrodynamics',
    functionDesc: 'Converts incident solar irradiance (photons) into DC electric power via the photoelectric effect.',
    equations: ['P_{pv} = G \\cdot A \\cdot \\eta_{cell}', 'I = I_{ph} - I_0 (e^{\\frac{q V}{k T}} - 1)'],
    connections: ['controller'],
    energyFlowOrder: 1,
  };

  // 3. MPPT Charge Controller
  const ctrlGeo = new THREE.BoxGeometry(0.8, 0.4, 0.8);
  const ctrlMat = new THREE.MeshStandardMaterial({ color: 0x2563eb, metalness: 0.5, roughness: 0.3 });
  const ctrl = new THREE.Mesh(ctrlGeo, ctrlMat);
  ctrl.position.set(1.2, 0.9, 0);
  ctrl.name = 'controller';
  group.add(ctrl);
  components['controller'] = {
    id: 'controller',
    name: 'MPPT Charge Controller (Buck-Boost DC-DC)',
    domain: 'Electrical Engineering & Control Theory',
    functionDesc: 'Executes perturb-and-observe maximum power point tracking to maximize impedance matching between PV array and battery.',
    equations: ['\\frac{dP}{dV} = 0', 'V_{out} = \\frac{D}{1 - D} V_{in}'],
    connections: ['solar_panel', 'battery'],
    energyFlowOrder: 2,
  };

  // 4. Lithium-Ion Battery Pack
  const battGeo = new THREE.BoxGeometry(1.6, 0.6, 1.2);
  const battMat = new THREE.MeshStandardMaterial({ color: 0x059669, metalness: 0.4, roughness: 0.4 });
  const batt = new THREE.Mesh(battGeo, battMat);
  batt.position.set(0, 0.9, 0);
  batt.name = 'battery';
  group.add(batt);
  components['battery'] = {
    id: 'battery',
    name: 'LiFePO4 Energy Storage Pack',
    domain: 'Electrochemistry & Thermodynamics',
    functionDesc: 'Stores chemical potential energy to buffer fluctuating solar irradiance and deliver instantaneous peak drive current.',
    equations: ['E_{stored} = \\int V(t) \\cdot I(t) dt', 'V_{cell} = E^0 - \\frac{R T}{n F} \\ln Q'],
    connections: ['controller', 'motor'],
    energyFlowOrder: 3,
  };

  // 5. High-Torque BLDC Electric Motor
  const motorGeo = new THREE.CylinderGeometry(0.5, 0.5, 0.9, 24);
  const motorMat = new THREE.MeshStandardMaterial({ color: 0xd97706, metalness: 0.7, roughness: 0.2 });
  const motor = new THREE.Mesh(motorGeo, motorMat);
  motor.rotation.z = Math.PI / 2;
  motor.position.set(-1.8, 0.6, 0);
  motor.name = 'motor';
  group.add(motor);
  components['motor'] = {
    id: 'motor',
    name: 'Axial-Flux Permanent Magnet Synchronous Motor',
    domain: 'Electrodynamics & Mechanical Engineering',
    functionDesc: 'Converts electrical power into rotational electromagnetic torque through Lorentz magnetic force interaction.',
    equations: ['\\tau = K_t \\cdot I', 'P_{mech} = \\tau \\cdot \\omega = P_{elec} \\cdot \\eta_{motor}'],
    connections: ['battery', 'wheels'],
    energyFlowOrder: 4,
  };

  // 6. Wheels and Regenerative Hubs
  const wheelGeo = new THREE.CylinderGeometry(0.6, 0.6, 0.35, 24);
  const wheelMat = new THREE.MeshStandardMaterial({ color: 0x1f2937, roughness: 0.8 });
  const wheelPositions = [
    [-2, 0.5, 1.5],
    [-2, 0.5, -1.5],
    [2, 0.5, 1.5],
    [2, 0.5, -1.5],
  ];
  wheelPositions.forEach((pos) => {
    const w = new THREE.Mesh(wheelGeo, wheelMat);
    w.rotation.x = Math.PI / 2;
    w.position.set(pos[0], pos[1], pos[2]);
    w.name = 'wheels';
    w.castShadow = true;
    group.add(w);
  });
  components['wheels'] = {
    id: 'wheels',
    name: 'Ultra-Low Rolling Resistance Wheels & Hubs',
    domain: 'Classical Mechanics & Tribology',
    functionDesc: 'Transfers rotational torque to pavement tractive force while minimizing rolling resistance losses.',
    equations: ['F_{traction} = \\frac{\\tau}{r}', 'F_{roll} = C_{rr} \\cdot N'],
    connections: ['motor', 'chassis'],
    energyFlowOrder: 5,
  };

  // 7. Animated Energy Flow Particles
  const particleCount = 40;
  const particleGeo = new THREE.BufferGeometry();
  const positions = new Float32Array(particleCount * 3);
  const particlePath = [
    new THREE.Vector3(0, 1.4, 0),     // Solar Panel
    new THREE.Vector3(1.2, 0.9, 0),   // Controller
    new THREE.Vector3(0, 0.9, 0),     // Battery
    new THREE.Vector3(-1.8, 0.6, 0),  // Motor
    new THREE.Vector3(-2, 0.5, 1.5),  // Wheels
  ];
  for (let i = 0; i < particleCount; i++) {
    positions[i * 3] = 0;
    positions[i * 3 + 1] = 0;
    positions[i * 3 + 2] = 0;
  }
  particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  const particleMat = new THREE.PointsMaterial({
    color: 0x38bdf8,
    size: 0.12,
    transparent: true,
    opacity: 0.9,
  });
  const particleSystem = new THREE.Points(particleGeo, particleMat);
  group.add(particleSystem);

  let progress = 0;
  const updateParticles = (delta: number) => {
    progress += delta * 0.4;
    const posAttr = particleGeo.attributes.position as THREE.BufferAttribute;
    for (let i = 0; i < particleCount; i++) {
      const t = (progress + i / particleCount) % 1;
      const totalSegments = particlePath.length - 1;
      const seg = Math.min(Math.floor(t * totalSegments), totalSegments - 1);
      const subT = (t * totalSegments) - seg;
      const p1 = particlePath[seg];
      const p2 = particlePath[seg + 1];
      posAttr.setXYZ(
        i,
        p1.x + (p2.x - p1.x) * subT,
        p1.y + (p2.y - p1.y) * subT,
        p1.z + (p2.z - p1.z) * subT
      );
    }
    posAttr.needsUpdate = true;
  };

  return {
    title: 'Solar-Powered Electric Drivetrain',
    description: 'Closed-loop multi-domain energy conversion from solar photons to kinetic tractive propulsion.',
    group,
    components,
    updateParticles,
  };
}

export function buildCircuitScene(): SceneModelData {
  const group = new THREE.Group();
  const components: Record<string, ComponentMetadata> = {};

  const baseGeo = new THREE.BoxGeometry(8, 0.3, 5);
  const baseMat = new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.6 });
  const base = new THREE.Mesh(baseGeo, baseMat);
  base.position.y = -0.15;
  base.receiveShadow = true;
  group.add(base);

  const battGeo = new THREE.CylinderGeometry(0.6, 0.6, 1.8, 20);
  const battMat = new THREE.MeshStandardMaterial({ color: 0x2563eb, metalness: 0.6, roughness: 0.3 });
  const batt = new THREE.Mesh(battGeo, battMat);
  batt.position.set(-2.5, 0.9, -1);
  batt.name = 'dc_source';
  group.add(batt);
  components['dc_source'] = {
    id: 'dc_source',
    name: 'DC Voltage Source (Electrochemical Cell)',
    domain: 'Electrodynamics & Electrochemistry',
    functionDesc: 'Maintains an electrostatic potential difference (voltage) across circuit terminals via chemical redox reactions.',
    equations: ['V = \\frac{W}{Q}', '\\mathcal{E} = \\oint \\vec{E} \\cdot d\\vec{l}'],
    connections: ['conductors', 'switch'],
  };

  const resGeo = new THREE.CylinderGeometry(0.35, 0.35, 1.5, 16);
  const resMat = new THREE.MeshStandardMaterial({ color: 0xd97706, roughness: 0.5 });
  const res = new THREE.Mesh(resGeo, resMat);
  res.rotation.z = Math.PI / 2;
  res.position.set(0, 0.4, 1.5);
  res.name = 'resistor';
  group.add(res);
  components['resistor'] = {
    id: 'resistor',
    name: 'Precision Dissipative Resistor',
    domain: 'Solid-State Physics & Circuit Theory',
    functionDesc: 'Dissipates electrical potential energy as Joule thermal heat via electron-phonon scattering.',
    equations: ['V = I \\cdot R', 'P_{loss} = I^2 R = \\frac{V^2}{R}'],
    connections: ['conductors', 'switch'],
  };

  const swGeo = new THREE.BoxGeometry(0.8, 0.4, 0.8);
  const swMat = new THREE.MeshStandardMaterial({ color: 0x475569, metalness: 0.8, roughness: 0.2 });
  const sw = new THREE.Mesh(swGeo, swMat);
  sw.position.set(2.5, 0.3, -1);
  sw.name = 'switch';
  group.add(sw);
  components['switch'] = {
    id: 'switch',
    name: 'Bi-Stable Mechanical Circuit Switch',
    domain: 'Circuit Theory & Control',
    functionDesc: 'Provides discrete boundary condition control: closed circuit (continuous path) vs open circuit (infinite dielectric air gap).',
    equations: ['I_{open} = 0', 'R_{contact} \\approx 0'],
    connections: ['dc_source', 'resistor'],
  };

  const traceMat = new THREE.MeshStandardMaterial({ color: 0xb45309, metalness: 0.9, roughness: 0.1 });
  const wire1 = new THREE.Mesh(new THREE.BoxGeometry(5.2, 0.05, 0.15), traceMat);
  wire1.position.set(0, 0.05, -1);
  group.add(wire1);
  const wire2 = new THREE.Mesh(new THREE.BoxGeometry(0.15, 0.05, 2.6), traceMat);
  wire2.position.set(2.5, 0.05, 0.25);
  group.add(wire2);
  const wire3 = new THREE.Mesh(new THREE.BoxGeometry(5.2, 0.05, 0.15), traceMat);
  wire3.position.set(0, 0.05, 1.5);
  group.add(wire3);
  const wire4 = new THREE.Mesh(new THREE.BoxGeometry(0.15, 0.05, 2.6), traceMat);
  wire4.position.set(-2.5, 0.05, 0.25);
  group.add(wire4);

  components['conductors'] = {
    id: 'conductors',
    name: 'High-Conductivity Copper Traces',
    domain: 'Materials Electrodynamics',
    functionDesc: 'Provides delocalized electron conduction band pathways with minimal Ohmic resistance.',
    equations: ['R = \\rho \\frac{L}{A}', '\\vec{J} = \\sigma \\vec{E}'],
    connections: ['dc_source', 'resistor', 'switch'],
  };

  const pCount = 30;
  const pGeo = new THREE.BufferGeometry();
  const posArr = new Float32Array(pCount * 3);
  pGeo.setAttribute('position', new THREE.BufferAttribute(posArr, 3));
  const pMat = new THREE.PointsMaterial({ color: 0x3b82f6, size: 0.14 });
  const pSystem = new THREE.Points(pGeo, pMat);
  group.add(pSystem);

  const loopWaypoints = [
    new THREE.Vector3(-2.5, 0.2, -1),
    new THREE.Vector3(2.5, 0.2, -1),
    new THREE.Vector3(2.5, 0.2, 1.5),
    new THREE.Vector3(-2.5, 0.2, 1.5),
  ];

  let pTime = 0;
  const updateParticles = (delta: number) => {
    pTime += delta * 0.5;
    const attr = pGeo.attributes.position as THREE.BufferAttribute;
    for (let i = 0; i < pCount; i++) {
      const t = (pTime + i / pCount) % 1;
      const seg = Math.floor(t * 4) % 4;
      const sub = (t * 4) - Math.floor(t * 4);
      const pA = loopWaypoints[seg];
      const pB = loopWaypoints[(seg + 1) % 4];
      attr.setXYZ(i, pA.x + (pB.x - pA.x) * sub, 0.2, pA.z + (pB.z - pA.z) * sub);
    }
    attr.needsUpdate = true;
  };

  return {
    title: 'Closed Electrical Circuit & Current Flow',
    description: 'Fundamental electrodynamic circuit governed by Ohm’s Law and Kirchhoff’s Current Conservation.',
    group,
    components,
    updateParticles,
  };
}

export function buildHydraulicScene(): SceneModelData {
  const group = new THREE.Group();
  const components: Record<string, ComponentMetadata> = {};

  const pipeGeo = new THREE.CylinderGeometry(1.2, 1.2, 8, 32, 1, true);
  const pipeMat = new THREE.MeshPhysicalMaterial({
    color: 0x93c5fd,
    transparent: true,
    opacity: 0.35,
    roughness: 0.1,
    transmission: 0.8,
    thickness: 0.5,
    side: THREE.DoubleSide,
  });
  const pipe = new THREE.Mesh(pipeGeo, pipeMat);
  pipe.rotation.z = Math.PI / 2;
  pipe.position.y = 1.5;
  pipe.name = 'pipe';
  group.add(pipe);
  components['pipe'] = {
    id: 'pipe',
    name: 'Cylindrical Conduit (No-Slip Wall Boundary)',
    domain: 'Fluid Mechanics & Navier-Stokes',
    functionDesc: 'Imposes zero-velocity Dirichlet boundary conditions at the radius perimeter (u(R) = 0).',
    equations: ['u(r) = \\frac{\\Delta P}{4 \\mu L} (R^2 - r^2)', 'Q = \\frac{\\pi R^4 \\Delta P}{8 \\mu L}'],
    connections: ['pressure_gradient', 'fluid_core'],
  };

  const mano1Geo = new THREE.CylinderGeometry(0.2, 0.2, 2.5, 16);
  const manoMat = new THREE.MeshStandardMaterial({ color: 0xef4444, roughness: 0.3 });
  const mano1 = new THREE.Mesh(mano1Geo, manoMat);
  mano1.position.set(-2.5, 2.8, 0);
  mano1.name = 'pressure_inlet';
  group.add(mano1);

  const mano2Geo = new THREE.CylinderGeometry(0.2, 0.2, 1.2, 16);
  const mano2 = new THREE.Mesh(mano2Geo, manoMat);
  mano2.position.set(2.5, 2.15, 0);
  mano2.name = 'pressure_outlet';
  group.add(mano2);

  components['pressure_gradient'] = {
    id: 'pressure_gradient',
    name: 'Hydrostatic Pressure Gradient (ΔP = P₁ - P₂)',
    domain: 'Thermodynamics & Fluid Dynamics',
    functionDesc: 'Provides the net driving thermodynamic force driving volumetric fluid transport against viscous drag.',
    equations: ['\\Delta P = P_1 - P_2 = R_{hyd} \\cdot Q', 'R_{hyd} = \\frac{8 \\mu L}{\\pi R^4}'],
    connections: ['pipe'],
  };

  const vectorGroup = new THREE.Group();
  for (let r = -0.9; r <= 0.9; r += 0.3) {
    const vel = 1.5 * (1 - (r * r) / (1.2 * 1.2));
    const arrow = new THREE.ArrowHelper(
      new THREE.Vector3(1, 0, 0),
      new THREE.Vector3(-0.5, 1.5 + r, 0),
      vel,
      0x2563eb,
      0.2,
      0.1
    );
    vectorGroup.add(arrow);
  }
  group.add(vectorGroup);
  components['fluid_core'] = {
    id: 'fluid_core',
    name: 'Hagen-Poiseuille Parabolic Laminar Streamlines',
    domain: 'Continuum Mechanics',
    functionDesc: 'Demonstrates maximum centerline laminar velocity and quadratic velocity degradation toward the pipe perimeter.',
    equations: ['v_{max} = 2 v_{avg}', '\\tau_w = \\mu \\left.\\frac{du}{dr}\\right|_{r=R}'],
    connections: ['pipe', 'pressure_gradient'],
  };

  return {
    title: 'Hydraulic Hagen-Poiseuille Continuum Flow',
    description: 'Exact analog to electrical conduction: Volumetric flow Q corresponds to current I, and ΔP corresponds to Voltage V.',
    group,
    components,
  };
}

export function buildMolecularScene(): SceneModelData {
  const group = new THREE.Group();
  const components: Record<string, ComponentMetadata> = {};

  const atomGeo = new THREE.SphereGeometry(0.4, 24, 24);
  const carbonMat = new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.3, metalness: 0.2 });
  const oxygenMat = new THREE.MeshStandardMaterial({ color: 0xdc2626, roughness: 0.3, metalness: 0.1 });
  const hydrogenMat = new THREE.MeshStandardMaterial({ color: 0x38bdf8, roughness: 0.2 });

  const centerAtom = new THREE.Mesh(atomGeo, carbonMat);
  centerAtom.position.set(0, 1.5, 0);
  centerAtom.name = 'central_atom';
  group.add(centerAtom);
  components['central_atom'] = {
    id: 'central_atom',
    name: 'Central Carbon/Silicon Core Atom (sp³ hybridized)',
    domain: 'Quantum Chemistry & Molecular Orbital Theory',
    functionDesc: 'Forms four equivalent tetrahedral hybrid orbitals with 109.5° bond angles for maximal valence electron stability.',
    equations: ['\\psi_{sp^3} = \\frac{1}{2} (\\psi_s + \\sqrt{3} \\psi_p)', 'E_{bond} = -\\int \\psi^* \\hat{H} \\psi d\\tau'],
    connections: ['covalent_bonds', 'ligand_atoms'],
  };

  const coords = [
    [1.4, 2.5, 1.4],
    [-1.4, 2.5, -1.4],
    [1.4, 0.5, -1.4],
    [-1.4, 0.5, 1.4],
  ];

  coords.forEach((c, idx) => {
    const mat = idx % 2 === 0 ? oxygenMat : hydrogenMat;
    const atom = new THREE.Mesh(atomGeo, mat);
    atom.position.set(c[0], c[1], c[2]);
    atom.name = `ligand_${idx}`;
    group.add(atom);

    const start = new THREE.Vector3(0, 1.5, 0);
    const end = new THREE.Vector3(c[0], c[1], c[2]);
    const dir = new THREE.Vector3().subVectors(end, start);
    const len = dir.length();
    const bondGeo = new THREE.CylinderGeometry(0.08, 0.08, len, 12);
    const bondMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.5 });
    const bond = new THREE.Mesh(bondGeo, bondMat);
    bond.position.copy(start).add(dir.clone().multiplyScalar(0.5));
    bond.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir.clone().normalize());
    group.add(bond);
  });

  components['covalent_bonds'] = {
    id: 'covalent_bonds',
    name: 'Covalent Sigma (σ) Electron Pairs',
    domain: 'Physical Chemistry & Solid-State Physics',
    functionDesc: 'Direct orbital head-on overlap creating localized electronic charge density between nuclei.',
    equations: ['V(r) = D_e (1 - e^{-a(r - r_e)})^2', 'k = \\left.\\frac{d^2 V}{dr^2}\\right|_{r=r_e}'],
    connections: ['central_atom'],
  };

  return {
    title: 'Tetrahedral Molecular Bonding Geometry',
    description: 'sp³ orbital hybridization minimizing Lennard-Jones intermolecular electrostatic repulsion.',
    group,
    components,
  };
}

export function buildCrossDomainGraphScene(): SceneModelData {
  const group = new THREE.Group();
  const components: Record<string, ComponentMetadata> = {};

  const domains = [
    { id: 'physics', name: 'Physics (Continuum & Electrodynamics)', color: 0x2563eb, pos: [-3, 2, 0] },
    { id: 'electrical', name: 'Electrical Engineering & Circuits', color: 0x059669, pos: [3, 2, 0] },
    { id: 'mechanical', name: 'Mechanical & Fluid Mechanics', color: 0xd97706, pos: [0, 4, -2] },
    { id: 'mathematics', name: 'Mathematics & Differential Systems', color: 0x7c3aed, pos: [0, 0.5, 2] },
  ];

  const nodeGeo = new THREE.SphereGeometry(0.7, 24, 24);

  domains.forEach((d) => {
    const mat = new THREE.MeshStandardMaterial({ color: d.color, roughness: 0.3, metalness: 0.4 });
    const mesh = new THREE.Mesh(nodeGeo, mat);
    mesh.position.set(d.pos[0], d.pos[1], d.pos[2]);
    mesh.name = d.id;
    group.add(mesh);

    components[d.id] = {
      id: d.id,
      name: d.name,
      domain: d.name,
      functionDesc: `Constitutive domain holding verified Tier 1 physical equations and ontological concepts.`,
      equations: ['\\nabla \\cdot \\vec{D} = \\rho', '\\nabla \\times \\vec{E} = -\\frac{\\partial \\vec{B}}{\\partial t}'],
      connections: domains.filter(o => o.id !== d.id).map(o => o.id),
    };
  });

  const edgeMat = new THREE.LineBasicMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.6 });
  for (let i = 0; i < domains.length; i++) {
    for (let j = i + 1; j < domains.length; j++) {
      const p1 = new THREE.Vector3(...domains[i].pos);
      const p2 = new THREE.Vector3(...domains[j].pos);
      const geo = new THREE.BufferGeometry().setFromPoints([p1, p2]);
      const line = new THREE.Line(geo, edgeMat);
      group.add(line);
    }
  }

  return {
    title: 'Cross-Domain Knowledge & Transfer Topology',
    description: 'Structural analogical mapping and applicability verification connecting disparate scientific branches.',
    group,
    components,
  };
}
