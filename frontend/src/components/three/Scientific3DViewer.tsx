import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import {
  RotateCcw,
  Zap,
  Layers,
} from 'lucide-react';
import {
  ComponentMetadata,
  SceneModelData,
  buildElectricMotorScene,
  buildPhotosynthesisScene,
  buildHydraulicLiftScene,
  buildSolarVehicleScene,
  buildCircuitScene,
  buildHydraulicScene,
  buildMolecularScene,
  buildCrossDomainGraphScene,
} from './scenes';

interface Props {
  initialScene?: string;
  queryContext?: string;
}

export const Scientific3DViewer: React.FC<Props> = ({ initialScene, queryContext }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [activeSceneKey, setActiveSceneKey] = useState<string>('electric_motor');
  const [selectedComp, setSelectedComp] = useState<ComponentMetadata | null>(null);
  const [flowActive, setFlowActive] = useState<boolean>(true);
  const [sceneTitle, setSceneTitle] = useState<string>('');
  const [sceneDesc, setSceneDesc] = useState<string>('');

  // Three.js refs
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const modelGroupRef = useRef<THREE.Group | null>(null);
  const updateParticlesRef = useRef<((delta: number) => void) | null>(null);
  const componentsMapRef = useRef<Record<string, ComponentMetadata>>({});

  // Auto-detect optimal scientific scene based on queryContext or initialScene
  useEffect(() => {
    if (initialScene) {
      setActiveSceneKey(initialScene);
      return;
    }
    if (queryContext) {
      const q = queryContext.toLowerCase();
      if (q.includes('motor') || q.includes('rotor') || q.includes('stator') || q.includes('electromagnet')) {
        setActiveSceneKey('electric_motor');
      } else if (q.includes('photosynthesis') || q.includes('chloroplast') || q.includes('plant') || q.includes('calvin')) {
        setActiveSceneKey('photosynthesis');
      } else if (q.includes('lift') || q.includes('pascal') || q.includes('hydraulic lift') || q.includes('jack')) {
        setActiveSceneKey('hydraulic_lift');
      } else if (q.includes('solar') || q.includes('car') || q.includes('vehicle') || q.includes('drivetrain')) {
        setActiveSceneKey('solar_vehicle');
      } else if (q.includes('circuit') || q.includes('resistor') || q.includes('ohm') || q.includes('current')) {
        setActiveSceneKey('circuit');
      } else if (q.includes('pipe') || q.includes('fluid') || q.includes('poiseuille') || q.includes('viscous')) {
        setActiveSceneKey('hydraulic');
      } else if (q.includes('molecule') || q.includes('chemical') || q.includes('atom') || q.includes('bond')) {
        setActiveSceneKey('molecular');
      } else {
        setActiveSceneKey('cross_domain_graph');
      }
    }
  }, [initialScene, queryContext]);

  // Initialize Three.js scene
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    // Scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xfcfdfd);
    sceneRef.current = scene;

    // Camera
    const camera = new THREE.PerspectiveCamera(
      45,
      container.clientWidth / container.clientHeight,
      0.1,
      1000
    );
    camera.position.set(10, 8, 10);
    camera.lookAt(0, 0, 0);
    cameraRef.current = camera;

    // Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    container.innerHTML = '';
    container.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // Subtle, Realistic Scientific Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.85);
    scene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(0xffffff, 0.9);
    dirLight1.position.set(12, 18, 12);
    dirLight1.castShadow = true;
    dirLight1.shadow.mapSize.width = 1024;
    dirLight1.shadow.mapSize.height = 1024;
    scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0x93c5fd, 0.4);
    dirLight2.position.set(-12, -8, -12);
    scene.add(dirLight2);

    // Subtle Ground Grid
    const groundGrid = new THREE.GridHelper(16, 16, 0xe2e8f0, 0xf1f5f9);
    groundGrid.position.y = -0.01;
    scene.add(groundGrid);

    // Load active scene data
    loadSceneModel(activeSceneKey);

    // Native Orbit & Pan Interaction Handling
    let isDragging = false;
    let isPanning = false;
    let prevMouseX = 0;
    let prevMouseY = 0;

    const onMouseDown = (e: MouseEvent) => {
      if (e.button === 0) isDragging = true;
      if (e.button === 2) isPanning = true;
      prevMouseX = e.clientX;
      prevMouseY = e.clientY;
    };

    const onMouseMove = (e: MouseEvent) => {
      if (!isDragging && !isPanning) return;
      const dx = e.clientX - prevMouseX;
      const dy = e.clientY - prevMouseY;
      prevMouseX = e.clientX;
      prevMouseY = e.clientY;

      if (isDragging && modelGroupRef.current) {
        modelGroupRef.current.rotation.y += dx * 0.008;
        modelGroupRef.current.rotation.x += dy * 0.008;
      } else if (isPanning && cameraRef.current) {
        cameraRef.current.position.x -= dx * 0.02;
        cameraRef.current.position.y += dy * 0.02;
      }
    };

    const onMouseUp = () => {
      isDragging = false;
      isPanning = false;
    };

    const onWheel = (e: WheelEvent) => {
      e.preventDefault();
      if (!cameraRef.current) return;
      const zoomFactor = e.deltaY * 0.01;
      cameraRef.current.position.multiplyScalar(1 + zoomFactor * 0.1);
      cameraRef.current.position.clampLength(3, 40);
    };

    // Raycaster for interactive component selection
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    const onClick = (e: MouseEvent) => {
      const rect = renderer.domElement.getBoundingClientRect();
      mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

      if (!cameraRef.current || !modelGroupRef.current) return;
      raycaster.setFromCamera(mouse, cameraRef.current);
      const intersects = raycaster.intersectObjects(modelGroupRef.current.children, true);

      if (intersects.length > 0) {
        let obj: THREE.Object3D | null = intersects[0].object;
        while (obj && !obj.name && obj.parent !== modelGroupRef.current) {
          obj = obj.parent;
        }
        if (obj && obj.name && componentsMapRef.current[obj.name]) {
          setSelectedComp(componentsMapRef.current[obj.name]);
          highlightMesh(obj);
        }
      }
    };

    const domEl = renderer.domElement;
    domEl.addEventListener('mousedown', onMouseDown);
    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
    domEl.addEventListener('wheel', onWheel, { passive: false });
    domEl.addEventListener('click', onClick);
    domEl.addEventListener('contextmenu', (e) => e.preventDefault());

    // Window resize observer
    const resizeObserver = new ResizeObserver(() => {
      if (!container || !renderer || !camera) return;
      camera.aspect = container.clientWidth / container.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(container.clientWidth, container.clientHeight);
    });
    resizeObserver.observe(container);

    // Animation Loop
    let animationFrameId: number;
    let clock = new THREE.Clock();

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      const delta = clock.getDelta();

      if (flowActive && updateParticlesRef.current) {
        updateParticlesRef.current(delta);
      }

      renderer.render(scene, camera);
    };
    animate();

    return () => {
      cancelAnimationFrame(animationFrameId);
      resizeObserver.disconnect();
      domEl.removeEventListener('mousedown', onMouseDown);
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
      domEl.removeEventListener('wheel', onWheel);
      domEl.removeEventListener('click', onClick);
      renderer.dispose();
    };
  }, [activeSceneKey, flowActive]);

  const loadSceneModel = (key: string) => {
    if (!sceneRef.current) return;

    if (modelGroupRef.current) {
      sceneRef.current.remove(modelGroupRef.current);
    }

    let sceneData: SceneModelData;
    if (key === 'electric_motor') sceneData = buildElectricMotorScene();
    else if (key === 'photosynthesis') sceneData = buildPhotosynthesisScene();
    else if (key === 'hydraulic_lift') sceneData = buildHydraulicLiftScene();
    else if (key === 'solar_vehicle') sceneData = buildSolarVehicleScene();
    else if (key === 'circuit') sceneData = buildCircuitScene();
    else if (key === 'hydraulic') sceneData = buildHydraulicScene();
    else if (key === 'molecular') sceneData = buildMolecularScene();
    else sceneData = buildCrossDomainGraphScene();

    setSceneTitle(sceneData.title);
    setSceneDesc(sceneData.description);
    componentsMapRef.current = sceneData.components;
    updateParticlesRef.current = sceneData.updateParticles || null;

    modelGroupRef.current = sceneData.group;
    sceneRef.current.add(sceneData.group);

    resetCamera();
    setSelectedComp(null);
  };

  const highlightMesh = (targetMesh: THREE.Object3D) => {
    targetMesh.scale.set(1.08, 1.08, 1.08);
    setTimeout(() => {
      targetMesh.scale.set(1, 1, 1);
    }, 250);
  };

  const resetCamera = () => {
    if (!cameraRef.current || !modelGroupRef.current) return;
    cameraRef.current.position.set(10, 8, 10);
    cameraRef.current.lookAt(0, 0, 0);
    modelGroupRef.current.rotation.set(0, 0, 0);
  };

  const setViewAngle = (angle: 'iso' | 'top' | 'front' | 'side') => {
    if (!cameraRef.current || !modelGroupRef.current) return;
    modelGroupRef.current.rotation.set(0, 0, 0);
    if (angle === 'iso') {
      cameraRef.current.position.set(11, 8, 11);
    } else if (angle === 'top') {
      cameraRef.current.position.set(0, 16, 0.001);
    } else if (angle === 'front') {
      cameraRef.current.position.set(0, 1.5, 14);
    } else if (angle === 'side') {
      cameraRef.current.position.set(14, 1.5, 0);
    }
    cameraRef.current.lookAt(0, 0, 0);
  };

  return (
    <div className="relative w-full rounded-2xl border border-gray-200 bg-white shadow-sm overflow-hidden my-6">
      {/* Top Controls & Scene Selector */}
      <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-3 border-b border-gray-100 bg-[#fbfbfc]">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-blue-600" />
          <span className="text-xs font-semibold uppercase tracking-wider text-gray-700">
            Interactive 3D Physical Model
          </span>
          <span className="text-xs text-gray-400">|</span>
          <span className="text-xs font-medium text-gray-900">{sceneTitle}</span>
        </div>

        {/* Scene Presets Selector */}
        <div className="flex items-center gap-1">
          <select
            value={activeSceneKey}
            onChange={(e) => setActiveSceneKey(e.target.value)}
            className="text-xs bg-white border border-gray-200 rounded-lg px-2.5 py-1 text-gray-700 font-medium hover:border-blue-500 focus:outline-none"
          >
            <option value="electric_motor">Electric Motor (Lorentz Torque)</option>
            <option value="photosynthesis">Photosynthesis (Chloroplast / Thylakoid)</option>
            <option value="hydraulic_lift">Hydraulic Lift (Pascal Principle)</option>
            <option value="solar_vehicle">Solar Vehicle Drivetrain</option>
            <option value="circuit">Electrical Circuit (Ohm)</option>
            <option value="hydraulic">Hydraulic Continuum (Poiseuille)</option>
            <option value="molecular">Molecular Tetrahedral (sp³)</option>
            <option value="cross_domain_graph">Cross-Domain Network</option>
          </select>
        </div>
      </div>

      {/* 3D WebGL Canvas Viewport */}
      <div className="relative w-full h-[460px] bg-gradient-to-b from-[#ffffff] to-[#f8f9fb]">
        <div ref={containerRef} className="w-full h-full cursor-grab active:cursor-grabbing" />

        {/* Viewport Floating Controls */}
        <div className="absolute top-3 left-3 flex flex-col gap-1.5 bg-white/90 backdrop-blur-sm border border-gray-200 rounded-xl p-1.5 shadow-xs">
          <button
            onClick={resetCamera}
            title="Reset Camera"
            className="p-1.5 text-gray-600 hover:text-blue-600 hover:bg-gray-50 rounded-lg text-xs flex items-center justify-center transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
          <button
            onClick={() => setViewAngle('iso')}
            title="Isometric View"
            className="px-2 py-1 text-[11px] font-semibold text-gray-600 hover:text-blue-600 hover:bg-gray-50 rounded-lg transition-colors"
          >
            ISO
          </button>
          <button
            onClick={() => setViewAngle('top')}
            title="Top/Plan View"
            className="px-2 py-1 text-[11px] font-semibold text-gray-600 hover:text-blue-600 hover:bg-gray-50 rounded-lg transition-colors"
          >
            TOP
          </button>
          <button
            onClick={() => setViewAngle('front')}
            title="Front View"
            className="px-2 py-1 text-[11px] font-semibold text-gray-600 hover:text-blue-600 hover:bg-gray-50 rounded-lg transition-colors"
          >
            FRT
          </button>
          <button
            onClick={() => setViewAngle('side')}
            title="Side View"
            className="px-2 py-1 text-[11px] font-semibold text-gray-600 hover:text-blue-600 hover:bg-gray-50 rounded-lg transition-colors"
          >
            SIDE
          </button>
        </div>

        {/* Dynamic Rotation / Motion Toggle */}
        <button
          onClick={() => setFlowActive(!flowActive)}
          className={`absolute bottom-3 left-3 flex items-center gap-1.5 px-3 py-1.5 rounded-xl border text-xs font-medium backdrop-blur-sm shadow-xs transition-colors ${
            flowActive
              ? 'bg-blue-50/95 border-blue-200 text-blue-700'
              : 'bg-white/90 border-gray-200 text-gray-600'
          }`}
        >
          <Zap className="w-3.5 h-3.5" />
          {flowActive ? 'Motion & Flux Active' : 'Motion Paused'}
        </button>

        {/* Quick Hint */}
        <div className="absolute bottom-3 right-3 text-[11px] text-gray-400 bg-white/80 backdrop-blur-xs px-2.5 py-1 rounded-md border border-gray-100 pointer-events-none">
          Click component to inspect • Drag to rotate • Scroll to zoom
        </div>

        {/* Selected Component Inspection Overlay Card */}
        {selectedComp && (
          <div className="absolute top-3 right-3 w-80 bg-white/95 backdrop-blur-md border border-blue-200 rounded-xl p-4 shadow-md text-left z-20">
            <div className="flex items-start justify-between gap-2 border-b border-gray-100 pb-2 mb-2">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full">
                  {selectedComp.domain}
                </span>
                <h4 className="text-sm font-semibold text-gray-900 mt-1">{selectedComp.name}</h4>
              </div>
              <button
                onClick={() => setSelectedComp(null)}
                className="text-gray-400 hover:text-gray-600 text-sm font-bold p-1"
              >
                &times;
              </button>
            </div>

            <p className="text-xs text-gray-600 leading-relaxed mb-3">
              {selectedComp.functionDesc}
            </p>

            {selectedComp.equations && selectedComp.equations.length > 0 && (
              <div className="mb-3">
                <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400 block mb-1">
                  Governing Principle / Formula
                </span>
                <div className="space-y-1">
                  {selectedComp.equations.map((eq, idx) => (
                    <div
                      key={idx}
                      className="text-xs font-mono bg-blue-50/50 text-blue-900 px-2 py-1 rounded border border-blue-100"
                    >
                      {eq}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {selectedComp.connections && selectedComp.connections.length > 0 && (
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400 block mb-1">
                  Interconnected Components
                </span>
                <div className="flex flex-wrap gap-1">
                  {selectedComp.connections.map((c) => (
                    <span
                      key={c}
                      className="text-[11px] bg-gray-100 text-gray-700 px-2 py-0.5 rounded-md font-mono"
                    >
                      &rarr; {c}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Description Footer */}
      <div className="px-4 py-2.5 bg-[#fbfbfc] border-t border-gray-100 text-xs text-gray-500 flex items-center justify-between">
        <span>{sceneDesc}</span>
        <span className="text-[11px] text-gray-400 font-mono">Three.js WebGL Engine</span>
      </div>
    </div>
  );
};
