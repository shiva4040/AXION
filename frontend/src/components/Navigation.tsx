import React, { useEffect, useRef, useState } from 'react';
import {
  Compass,
  History,
  ChevronDown,
  BookOpen,
  Share2,
  GitBranch,
  Repeat,
  FlaskConical,
  CheckCircle,
  Database,
  Cpu,
} from 'lucide-react';
import { WorkspaceId } from '../types';

interface Props {
  activeWorkspace: WorkspaceId;
  onSelectWorkspace: (ws: WorkspaceId) => void;
  onOpenHistory: () => void;
  onGoHome: () => void;
}

/* ------------------------------------------------------------------ */
/*  Motion tokens                                                       */
/* ------------------------------------------------------------------ */
const EXPO = 'cubic-bezier(0.16, 1, 0.3, 1)';
const SPRING = 'cubic-bezier(0.34, 1.56, 0.64, 1)';

/*
  Breakpoints used (plain CSS, so this works on Tailwind v3 and v4):
    < 360px   wordmark 18px
    >= 360px  wordmark 20px
    >= 480px  dropdown shows its text label (icon-only below)
    >= 640px  desktop layout: history button + API link return to the bar,
              dropdown is a popover instead of a bottom sheet
  Touch devices (pointer: coarse) get 44px hit areas and 44px menu rows.
*/
const NAV_CSS = `
/* ---------- layout, safe areas ---------- */
.axion-nav {
  height: calc(56px + env(safe-area-inset-top, 0px));
  padding-top: env(safe-area-inset-top, 0px);
  padding-left: max(12px, env(safe-area-inset-left, 0px));
  padding-right: max(12px, env(safe-area-inset-right, 0px));
  gap: 8px;
}
@media (min-width: 640px) {
  .axion-nav {
    padding-left: max(32px, env(safe-area-inset-left, 0px));
    padding-right: max(32px, env(safe-area-inset-right, 0px));
  }
}
.axion-nav button, .axion-nav a {
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
}

/* ---------- responsive type ---------- */
.axion-word { font-size: 18px; }
@media (min-width: 360px) { .axion-word { font-size: 20px; } }
@media (min-width: 640px) { .axion-word { font-size: 26px; } }

.axion-label {
  display: none;
  max-width: 90px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
@media (min-width: 480px) { .axion-label { display: inline-block; } }
@media (min-width: 640px) { .axion-label { max-width: none; } }

/* ---------- touch targets: visible size stays, hit area grows to 44px ---------- */
.axion-hit { position: relative; }
@media (pointer: coarse) {
  .axion-hit::before {
    content: '';
    position: absolute;
    inset: -6px;
  }
  .axion-hit-switch::before { inset: -12px -6px; }
  .axion-item { min-height: 44px; }
}

/* ---------- hover effects only where hover exists; :active gives tap feedback ---------- */
.axion-btn:active { background-color: #fff; }
.axion-item:active { background-color: #EFE6D2; }
@media (hover: hover) {
  .axion-btn:hover { background-color: #fff; }
  .axion-item:hover { background-color: #EFE6D2; padding-left: 16px; }
  .axion-home:hover .axion-letter { transform: translateY(-3px); }
  .axion-hist:hover svg { transform: rotate(-360deg); }
  .axion-api:hover .axion-api-arrow { transform: translate(2px, -2px); }
  .axion-api:hover .axion-api-line { transform: scaleX(1); }
}

/* ---------- dropdown: popover on desktop, bottom sheet on phones ---------- */
.axion-menu {
  max-height: 80vh;
  max-height: 80dvh;
  padding-top: 4px;
  padding-bottom: 4px;
  animation: axion-menu-in 340ms ${EXPO} both;
}
.axion-menu[data-phase="closing"] { animation: axion-menu-out 160ms ease-in both; }
.axion-backdrop { animation: axion-fade-in 260ms ease both; }
.axion-backdrop[data-phase="closing"] { animation: axion-fade-out 200ms ease both; }

@media (max-width: 639px) {
  .axion-menu {
    padding-bottom: max(4px, env(safe-area-inset-bottom, 0px));
    animation-name: axion-sheet-in;
    animation-duration: 420ms;
  }
  .axion-menu[data-phase="closing"] {
    animation-name: axion-sheet-out;
    animation-duration: 210ms;
  }
}

/* ---------- keyframes ---------- */
@keyframes axion-type {
  from { opacity: 0; transform: translateY(-14px) rotate(-6deg); }
  to   { opacity: 1; transform: none; }
}
@keyframes axion-stamp {
  0%   { transform: scale(1.9) rotate(-10deg); opacity: 0; }
  55%  { transform: scale(0.92) rotate(-1deg); opacity: 1; }
  100% { transform: scale(1) rotate(-2deg); opacity: 1; }
}
@keyframes axion-ring {
  from { transform: scale(1); opacity: 0.7; }
  to   { transform: scale(1.5, 2.1); opacity: 0; }
}
@keyframes axion-sweep {
  0%   { transform: scaleX(0); opacity: 1; }
  65%  { transform: scaleX(1); opacity: 1; }
  100% { transform: scaleX(1); opacity: 0; }
}
@keyframes axion-icon-pop {
  0%   { transform: scale(0.4) rotate(-40deg); opacity: 0; }
  65%  { transform: scale(1.18) rotate(8deg); opacity: 1; }
  100% { transform: scale(1) rotate(0); opacity: 1; }
}
@keyframes axion-menu-in {
  from { opacity: 0; transform: translateY(-6px); clip-path: inset(0 -10px 100% -10px); }
  to   { opacity: 1; transform: none; clip-path: inset(-4px -10px -10px -10px); }
}
@keyframes axion-menu-out {
  from { opacity: 1; transform: none; }
  to   { opacity: 0; transform: translateY(-6px) scale(0.98); }
}
@keyframes axion-sheet-in {
  from { transform: translateY(100%); }
  to   { transform: none; }
}
@keyframes axion-sheet-out {
  from { transform: none; }
  to   { transform: translateY(100%); }
}
@keyframes axion-fade-in  { from { opacity: 0; } to { opacity: 1; } }
@keyframes axion-fade-out { from { opacity: 1; } to { opacity: 0; } }
@keyframes axion-item {
  from { opacity: 0; transform: translateX(12px); }
  to   { opacity: 1; transform: none; }
}
@keyframes axion-unfurl-in {
  from { opacity: 0; transform: translateX(28px) scale(0.94); }
  to   { opacity: 1; transform: none; }
}
@keyframes axion-unfurl-out {
  from { opacity: 1; transform: none; }
  to   { opacity: 0; transform: translateX(28px) scale(0.94); }
}

@media (prefers-reduced-motion: reduce) {
  .axion-nav, .axion-nav * {
    animation-duration: 0.01ms !important;
    animation-delay: 0s !important;
    transition-duration: 0.01ms !important;
  }
}
`;

/* Label "decodes" from noise into the real name, left to right. */
function useScramble(target: string, duration = 420) {
  const [text, setText] = useState(target);
  useEffect(() => {
    if (typeof window !== 'undefined' && window.matchMedia?.('(prefers-reduced-motion: reduce)').matches) {
      setText(target);
      return;
    }
    const glyphs = '01<>/\\=+*#%';
    const start = performance.now();
    let raf = 0;
    const tick = (now: number) => {
      const p = Math.min(1, (now - start) / duration);
      const settled = Math.floor(p * target.length);
      setText(
        target
          .split('')
          .map((c, i) => (c === ' ' || i < settled ? c : glyphs[Math.floor(Math.random() * glyphs.length)]))
          .join('')
      );
      if (p < 1) raf = requestAnimationFrame(tick);
      else setText(target);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [target, duration]);
  return text;
}

type BarPhase = 'open' | 'closing' | 'closed';
type MenuPhase = 'closed' | 'open' | 'closing';

export const Navigation: React.FC<Props> = ({
  activeWorkspace,
  onSelectWorkspace,
  onOpenHistory,
  onGoHome,
}) => {
  const [hideTopBar, setHideTopBar] = useState<boolean>(() => {
    try {
      return localStorage.getItem('axion_hide_top_bar') === 'true';
    } catch {
      return false;
    }
  });
  const [barPhase, setBarPhase] = useState<BarPhase>(hideTopBar ? 'closed' : 'open');
  const [animateBar, setAnimateBar] = useState(false); // skip unfurl on first paint
  const [menuPhase, setMenuPhase] = useState<MenuPhase>('closed');
  const barTimer = useRef<number | undefined>(undefined);
  const menuTimer = useRef<number | undefined>(undefined);

  useEffect(
    () => () => {
      window.clearTimeout(barTimer.current);
      window.clearTimeout(menuTimer.current);
    },
    []
  );

  const menuMounted = menuPhase !== 'closed';

  // Escape closes the menu
  useEffect(() => {
    if (menuPhase !== 'open') return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') closeMenu();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [menuPhase]);

  // On phones the menu is a bottom sheet: stop the page scrolling behind it
  useEffect(() => {
    if (!menuMounted) return;
    if (!window.matchMedia('(max-width: 639px)').matches) return;
    const prev = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = prev;
    };
  }, [menuMounted]);

  const openMenu = () => {
    window.clearTimeout(menuTimer.current);
    setMenuPhase('open');
  };
  const closeMenu = () => {
    if (menuPhase !== 'open') return;
    setMenuPhase('closing');
    window.clearTimeout(menuTimer.current);
    menuTimer.current = window.setTimeout(() => setMenuPhase('closed'), 220);
  };

  const toggleHideTopBar = () => {
    const next = !hideTopBar;
    setHideTopBar(next);
    setAnimateBar(true);
    try {
      localStorage.setItem('axion_hide_top_bar', String(next));
    } catch {
      /* storage unavailable, ignore */
    }
    window.clearTimeout(barTimer.current);
    if (next) {
      window.clearTimeout(menuTimer.current);
      setMenuPhase('closed');
      setBarPhase('closing');
      barTimer.current = window.setTimeout(() => setBarPhase('closed'), 560);
    } else {
      setBarPhase('open');
    }
  };

  const workspaces: Array<{ id: WorkspaceId; label: string; icon: React.ReactNode; desc: string }> = [
    { id: 'ask', label: 'Ask AXION', icon: <Compass className="w-3.5 h-3.5" />, desc: 'Primary scientific query workstation' },
    { id: 'library', label: 'Knowledge Library', icon: <BookOpen className="w-3.5 h-3.5" />, desc: 'Ingested papers & trust tiers' },
    { id: 'graph', label: 'Knowledge Graph', icon: <Share2 className="w-3.5 h-3.5" />, desc: 'Concept network & dimensional paths' },
    { id: 'assistant', label: 'Research Assistant', icon: <Cpu className="w-3.5 h-3.5" />, desc: 'Advanced scientific investigations' },
    { id: 'reasoning', label: 'Reasoning Workspace', icon: <GitBranch className="w-3.5 h-3.5" />, desc: 'Goal decomposition DAG & contradictions' },
    { id: 'transfer', label: 'Cross-Domain Transfer', icon: <Repeat className="w-3.5 h-3.5" />, desc: 'Structural alignment & applicability guard' },
    { id: 'hypothesis', label: 'Hypothesis Lab', icon: <FlaskConical className="w-3.5 h-3.5" />, desc: 'Tier 3 conjectured formal hypothesis generator' },
    { id: 'validation', label: 'Experiment & Validation', icon: <CheckCircle className="w-3.5 h-3.5" />, desc: 'Sandbox symbolic, numerical, and ODE tests' },
    { id: 'memory', label: 'Validated Knowledge Memory', icon: <Database className="w-3.5 h-3.5" />, desc: 'Tier 4 persistent validated findings' },
    { id: 'history', label: 'Research History', icon: <History className="w-3.5 h-3.5" />, desc: 'Timeline and replay of past investigations' },
  ];

  const currentWs = workspaces.find((w) => w.id === activeWorkspace) || workspaces[0];
  const buttonLabel = currentWs.id === 'ask' ? 'Ask AXION' : currentWs.label;
  const scrambled = useScramble(buttonLabel);

  /* Index 0 sits next to the switch. Unfurl: nearest the switch first. Fold: farthest first. */
  const unfurl = (indexFromSwitch: number): React.CSSProperties => {
    if (!animateBar) return {};
    if (barPhase === 'closing') {
      return { animation: `axion-unfurl-out 320ms ${(3 - indexFromSwitch) * 55}ms ${EXPO} both` };
    }
    return { animation: `axion-unfurl-in 520ms ${indexFromSwitch * 70}ms ${EXPO} backwards` };
  };

  const itemBase =
    'axion-item w-full text-left px-3 py-2 flex items-center gap-2.5 text-[13px] sm:text-xs font-mono cursor-pointer transition-[padding,background-color] duration-200';
  const itemAnim = (i: number): React.CSSProperties | undefined =>
    menuPhase === 'open' ? { animation: `axion-item 380ms ${60 + i * 28}ms ${EXPO} backwards` } : undefined;

  return (
    <header
      className={`axion-nav w-full flex items-center justify-between sticky top-0 z-40 select-none ${hideTopBar
        ? 'bg-transparent border-b-[1.5px] border-transparent'
        : 'bg-[#E6DBC0] border-b-[1.5px] border-[#211E19]'
        }`}
      style={{ transition: `background-color 500ms ${EXPO}, border-color 500ms ${EXPO}` }}
    >
      <style>{NAV_CSS}</style>

      {/* Press pass: a red line travels along the bottom rule on each workspace change */}
      {!hideTopBar && (
        <span
          key={`sweep-${activeWorkspace}`}
          aria-hidden
          className="pointer-events-none absolute left-0 right-0 -bottom-[1.5px] h-[2px] bg-[#B83A22]"
          style={{
            opacity: 0,
            transformOrigin: 'left',
            animation: `axion-sweep 800ms ${EXPO} backwards`,
          }}
        />
      )}

      {/* Left: AXION wordmark & red INTELLIGENCE stamp (always visible) */}
      <div className="flex items-center gap-3 min-w-0">
        <button
          onClick={onGoHome}
          className="axion-home axion-hit flex items-center gap-2 sm:gap-2.5 text-left focus:outline-none cursor-pointer min-w-0"
        >
          <span
            className="axion-word text-[#211E19] font-black tracking-[0.06em] leading-none"
            style={{ fontFamily: 'var(--font-slab)' }}
            aria-label="AXION"
          >
            {'AXION'.split('').map((ch, i) => (
              <span
                key={i}
                aria-hidden
                className="axion-letter inline-block"
                style={{
                  animation: `axion-type 650ms ${i * 70}ms ${SPRING} backwards`,
                  transition: `transform 320ms ${SPRING}`,
                  transitionDelay: `${i * 45}ms`,
                }}
              >
                {ch}
              </span>
            ))}
          </span>

          <span
            key={activeWorkspace}
            className="relative whitespace-nowrap font-mono text-[8px] sm:text-[10px] font-bold uppercase tracking-widest text-[#B83A22] border-[1.5px] border-[#B83A22] px-1.5 py-0.5 bg-[#E6DBC0] shadow-[1px_1px_0px_#B83A22]"
            style={{
              transform: 'rotate(-2deg)',
              animation: `axion-stamp 520ms ${EXPO} both`,
            }}
          >
            INTELLIGENCE
            <span
              aria-hidden
              className="pointer-events-none absolute -inset-[1.5px] border-[1.5px] border-[#B83A22]"
              style={{ opacity: 0, animation: `axion-ring 750ms 180ms ${EXPO} backwards` }}
            />
          </span>
        </button>
      </div>

      {/* Right controls */}
      <div className="flex items-center gap-3 shrink-0">
        {barPhase !== 'closed' && (
          <div className={`flex items-center gap-3 ${barPhase === 'closing' ? 'pointer-events-none' : ''}`}>
            {/* Workspace dropdown (icon-only under 480px) */}
            <div className="relative" style={unfurl(3)}>
              <button
                onClick={() => (menuPhase === 'open' ? closeMenu() : openMenu())}
                aria-expanded={menuPhase === 'open'}
                aria-haspopup="true"
                aria-label={`Workspace: ${buttonLabel}`}
                className="axion-btn axion-hit h-8 px-3 bg-[#FBF5E6] text-[#211E19] border-2 border-[#211E19] shadow-[2px_2px_0px_#211E19] active:translate-x-[1px] active:translate-y-[1px] active:shadow-none flex items-center gap-2 text-xs font-mono font-medium transition-none cursor-pointer whitespace-nowrap"
              >
                <span
                  key={`icon-${activeWorkspace}`}
                  className="inline-flex shrink-0 [&>svg]:stroke-[2]"
                  style={{ animation: `axion-icon-pop 480ms ${SPRING} both` }}
                >
                  {currentWs.icon}
                </span>

                <span className="axion-label font-mono text-xs" aria-hidden>
                  {scrambled}
                </span>

                <ChevronDown
                  className="w-3 h-3 shrink-0 text-[#211E19] ml-0.5 stroke-[2]"
                  style={{
                    transform: menuPhase === 'open' ? 'rotate(180deg)' : 'rotate(0deg)',
                    transition: `transform 420ms ${SPRING}`,
                  }}
                />
              </button>

              {menuMounted && (
                <>
                  <div
                    data-phase={menuPhase}
                    className={`axion-backdrop fixed inset-0 z-40 bg-[#211E19]/40 sm:bg-transparent ${menuPhase === 'closing' ? 'pointer-events-none' : ''
                      }`}
                    onClick={closeMenu}
                  />
                  <div
                    data-phase={menuPhase}
                    className="axion-menu fixed bottom-0 left-0 right-0 w-full sm:absolute sm:left-auto sm:bottom-auto sm:right-0 sm:mt-1.5 sm:w-64 bg-[#FBF5E6] border-t-2 border-[#211E19] sm:border-2 sm:shadow-[4px_4px_0px_#211E19] z-50 overflow-y-auto overscroll-contain origin-top-right"
                  >
                    {/* Grab handle: phone sheet only */}
                    <div className="sm:hidden flex justify-center pt-1.5 pb-1" aria-hidden>
                      <span className="block w-10 h-1 bg-[#211E19]/30" />
                    </div>

                    <div className="px-3 py-1.5 text-[10px] font-mono font-bold uppercase tracking-widest text-[#70695D] border-b border-[#211E19]/20">
                      SYSTEM WORKSPACES
                    </div>

                    {workspaces.map((ws, i) => (
                      <button
                        key={ws.id}
                        onClick={() => {
                          onSelectWorkspace(ws.id);
                          closeMenu();
                        }}
                        className={`${itemBase} ${activeWorkspace === ws.id ? 'bg-[#E6DBC0] font-bold text-[#211E19]' : 'text-[#70695D]'
                          }`}
                        style={itemAnim(i)}
                      >
                        <span className="shrink-0">{ws.icon}</span>
                        <span className="truncate">{ws.label}</span>
                      </button>
                    ))}

                    {/* Phones only: these two controls live in the sheet instead of the bar */}
                    <div className="sm:hidden border-t border-[#211E19]/20 mt-1 pt-1">
                      <button
                        onClick={() => {
                          onOpenHistory();
                          closeMenu();
                        }}
                        className={`${itemBase} text-[#70695D]`}
                        style={itemAnim(workspaces.length)}
                      >
                        <History className="w-3.5 h-3.5 shrink-0" />
                        <span className="truncate">Investigation History</span>
                      </button>
                      <a
                        href="/docs"
                        target="_blank"
                        rel="noreferrer"
                        onClick={closeMenu}
                        className={`${itemBase} text-[#70695D]`}
                        style={itemAnim(workspaces.length + 1)}
                      >
                        <span className="w-3.5 shrink-0 text-center">↗</span>
                        <span className="truncate">API Docs</span>
                      </a>
                    </div>
                  </div>
                </>
              )}
            </div>

            {/* Square history button (640px and up) */}
            <div className="hidden sm:block" style={unfurl(2)}>
              <button
                onClick={onOpenHistory}
                className="axion-btn axion-hist axion-hit w-8 h-8 bg-[#FBF5E6] text-[#211E19] border-2 border-[#211E19] shadow-[2px_2px_0px_#211E19] active:translate-x-[1px] active:translate-y-[1px] active:shadow-none flex items-center justify-center transition-none cursor-pointer shrink-0"
                title="Investigation History"
                aria-label="Investigation History"
              >
                <History
                  className="w-3.5 h-3.5 stroke-[2]"
                  style={{ transition: `transform 700ms ${EXPO}` }}
                />
              </button>
            </div>

            {/* API link (640px and up) */}
            <div className="hidden sm:block shrink-0" style={unfurl(1)}>
              <a
                href="/docs"
                target="_blank"
                rel="noreferrer"
                className="axion-api relative font-mono text-xs font-bold uppercase tracking-wider text-[#211E19] px-1 py-1 flex items-center gap-0.5 ml-1 whitespace-nowrap"
                title="Open FastAPI Swagger Documentation"
              >
                <span>API</span>
                <span
                  className="axion-api-arrow inline-block"
                  style={{ transition: `transform 300ms ${SPRING}` }}
                >
                  ↗
                </span>
                <span
                  className="axion-api-line absolute left-1 right-1 bottom-0 h-[1.5px] bg-[#211E19] origin-left scale-x-0"
                  style={{ transition: `transform 380ms ${EXPO}` }}
                />
              </a>
            </div>

            {/* Divider (640px and up) */}
            <span
              className="hidden sm:block w-[1.5px] h-4 bg-[#211E19]/20 mx-0.5 shrink-0"
              style={unfurl(0)}
            />
          </div>
        )}

        {/* Vintage slide switch: knob travels with a springy overshoot */}
        <button
          type="button"
          role="switch"
          aria-checked={hideTopBar}
          onClick={toggleHideTopBar}
          className={`axion-hit axion-hit-switch w-10 h-5 border-2 border-[#211E19] p-0.5 flex items-center cursor-pointer shadow-[1.5px_1.5px_0px_#211E19] shrink-0 ${hideTopBar ? 'bg-[#211E19]' : 'bg-[#FBF5E6]'
            }`}
          style={{ transition: `background-color 400ms ${EXPO}` }}
          title={hideTopBar ? 'Show full top bar' : 'Hide top bar, show logo only'}
          aria-label={hideTopBar ? 'Show full top bar' : 'Hide top bar, show logo only'}
        >
          <div
            className={`w-3.5 h-3.5 border border-[#211E19] ${hideTopBar ? 'bg-[#B83A22] translate-x-5' : 'bg-[#70695D] translate-x-0'
              }`}
            style={{ transition: `transform 480ms ${SPRING}, background-color 300ms ${EXPO}` }}
          />
        </button>
      </div>
    </header>
  );
};