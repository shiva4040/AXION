import React, { useState, useRef, useEffect } from 'react';
import { Paperclip, ArrowUp, X, FileText, AlertCircle } from 'lucide-react';
import { ingestText } from '../api/client';

interface Props {
  onSubmitQuestion: (query: string, documentId?: string) => void;
  isLoading: boolean;
}

/* ------------------------------------------------------------------ */
/*  Motion tokens (same as Navigation.tsx)                              */
/* ------------------------------------------------------------------ */
const EXPO = 'cubic-bezier(0.16, 1, 0.3, 1)';
const SPRING = 'cubic-bezier(0.34, 1.56, 0.64, 1)';

const PLACEHOLDER = 'What would you like to understand or solve?';

/* Phone-only copy. Edit freely. */
const PHONE_PLACEHOLDER = 'Ask AXION anything';
const SUGGESTIONS = [
  'Why does entropy always increase?',
  'Connect an idea from physics to biology',
  'Test whether my hypothesis holds up',
];

/*
  Layouts:
    >= 640px  original desktop layout (query box with title strip and action strip)
    <  640px  chatbot layout: centered greeting + suggestion chips, and a pill
              composer docked to the bottom of the screen
              [ attach ] [ auto-growing text ] [ send ]
  The docked composer follows the on-screen keyboard (visualViewport) and
  respects the iPhone home-indicator safe area.
*/
const HOME_CSS = `
/* ---------- shared ---------- */
.hp-root {
  padding-top: 24px;
  padding-bottom: max(24px, env(safe-area-inset-bottom, 0px));
  padding-left: max(12px, env(safe-area-inset-left, 0px));
  padding-right: max(12px, env(safe-area-inset-right, 0px));
}
@media (min-width: 640px) {
  .hp-root {
    padding-top: 32px;
    padding-bottom: max(32px, env(safe-area-inset-bottom, 0px));
    padding-left: max(24px, env(safe-area-inset-left, 0px));
    padding-right: max(24px, env(safe-area-inset-right, 0px));
  }
}
.hp-root button {
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
}
.hp-hero { font-size: clamp(40px, min(13.5vw, 17vh), 76px); }

/* ---------- desktop box ---------- */
.hp-textarea { font-size: 15px; }
.hp-pad { min-height: 125px; }
@media (max-height: 480px) { .hp-pad { min-height: 72px; } }

.hp-hit { position: relative; }
@media (pointer: coarse) {
  .hp-hit::before { content: ''; position: absolute; inset: -6px; }
  .hp-hit-x::before { inset: -12px; }
  .hp-circle.hp-hit::before { inset: -2px; }
}

.hp-editor { transition: box-shadow 320ms ${EXPO}, transform 320ms ${SPRING}; }
.hp-editor:focus-within {
  box-shadow: 9px 9px 0 #211E19;
  transform: translate(-3px, -3px);
}

.hp-stripes {
  background-image: linear-gradient(to bottom, transparent 0, transparent 2px, #211E19 2px, #211E19 3px);
  background-size: 100% 3px;
}
.hp-stripes[data-busy="true"] { animation: hp-stripes 700ms linear infinite; }
.hp-dash[data-busy="true"]    { animation: hp-spin 900ms linear infinite; }
.hp-arrow[data-busy="true"]   { animation: hp-arrow-loop 900ms ease-in infinite; }

.hp-btn:not(:disabled):active { background-color: #fff; }
.hp-send-on:active { background-color: #9F301B; }
@media (hover: hover) {
  .hp-btn:not(:disabled):hover { background-color: #fff; }
  .hp-send-on:hover { background-color: #9F301B; }
  .hp-hero-wrap:hover .hp-letter { transform: translateY(-4px); }
  .hp-attach:not(:disabled):hover .hp-clip { transform: rotate(-24deg) translateY(-1px); }
  .hp-send-on:hover .hp-arrow { transform: translateY(-2px); }
  .hp-x:hover { color: #000; }
}

/* ---------- phone: chatbot layout ---------- */
.hp-phone-root {
  min-height: calc(100vh - 56px - env(safe-area-inset-top, 0px));
  min-height: calc(100dvh - 56px - env(safe-area-inset-top, 0px));
  padding-bottom: calc(var(--hp-dock-h, 84px) + 16px);
}

.hp-chips {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
  max-width: 360px;
  margin-top: 22px;
  transition: opacity 250ms ease, transform 350ms ${EXPO};
}
.hp-chips[data-hidden="true"] {
  opacity: 0;
  transform: translateY(-6px);
  pointer-events: none;
}
.hp-chip {
  border: 1.5px solid #211E19;
  border-radius: 999px;
  background: #FBF5E6;
  color: #211E19;
  font-size: 12px;
  line-height: 1.2;
  padding: 9px 14px;
  box-shadow: 1.5px 1.5px 0 #211E19;
  text-align: left;
  cursor: pointer;
}
.hp-chip:active { transform: translate(1px, 1px); box-shadow: none; background: #fff; }

.hp-dock {
  position: fixed;
  left: 0;
  right: 0;
  bottom: var(--hp-kb, 0px);
  z-index: 30;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 8px max(12px, env(safe-area-inset-right, 0px)) max(12px, env(safe-area-inset-bottom, 0px)) max(12px, env(safe-area-inset-left, 0px));
  pointer-events: none;
  animation: hp-dock-in 700ms 500ms ${EXPO} backwards;
}
.hp-dock > * { pointer-events: auto; }
.hp-phone-root[data-kb="true"] .hp-dock { padding-bottom: 8px; }

.hp-pill {
  position: relative;
  display: flex;
  align-items: flex-end;
  gap: 6px;
  padding: 6px;
  background: #FBF5E6;
  border: 2px solid #211E19;
  border-radius: 28px;
  box-shadow: 3px 3px 0 #211E19;
  overflow: hidden;
  transition: box-shadow 300ms ${EXPO}, transform 300ms ${SPRING};
}
.hp-pill:focus-within {
  box-shadow: 5px 5px 0 #211E19;
  transform: translate(-1px, -1px);
}
.hp-pill-ta {
  flex: 1;
  min-width: 0;
  max-height: 140px;
  padding: 9px 4px;
  font-size: 16px;
  line-height: 1.4;
  color: #211E19;
  background: transparent;
  border: none;
  outline: none;
  resize: none;
}
.hp-circle {
  position: relative;
  flex: none;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #211E19;
  border-radius: 999px;
  background: #F3EAD3;
  color: #211E19;
  cursor: pointer;
  transition: transform 220ms ${SPRING}, background-color 250ms ease, color 250ms ease, opacity 200ms ease;
}
.hp-circle:disabled { opacity: 0.5; }
.hp-circle:not(:disabled):active { transform: scale(0.92); }
.hp-send { background: #E6DBC0; color: #70695D; opacity: 1; }
.hp-send:disabled { opacity: 1; }
.hp-send.hp-send-on, .hp-send[data-busy="true"] { background: #B83A22; color: #fff; }

/* ---------- entrances ---------- */
.hp-reveal   { animation: hp-reveal 800ms 380ms ${EXPO} backwards; }
.hp-pop      { animation: hp-pop 420ms ${SPRING}; }
.hp-badge-in { animation: hp-badge-in 460ms ${EXPO} both; }
.hp-badge-out{ animation: hp-badge-out 200ms ease-in both; }
.hp-error    { animation: hp-error-in 560ms ${EXPO} both; }
.hp-bar      { animation: hp-indeterminate 1200ms ease-in-out infinite; }

@keyframes hp-type {
  from { opacity: 0; transform: translateY(-18px) rotate(-6deg); }
  to   { opacity: 1; transform: none; }
}
@keyframes hp-reveal {
  from { opacity: 0; clip-path: inset(0 0 100% 0); }
  to   { opacity: 1; clip-path: inset(-14px -14px -14px -14px); }
}
@keyframes hp-dock-in {
  from { opacity: 0; transform: translateY(48px); }
  to   { opacity: 1; transform: none; }
}
@keyframes hp-chip-in {
  from { opacity: 0; transform: translateY(12px) scale(0.96); }
  to   { opacity: 1; transform: none; }
}
@keyframes hp-stripes { from { background-position: 0 0; } to { background-position: 0 3px; } }
@keyframes hp-spin    { to { transform: rotate(360deg); } }
@keyframes hp-arrow-loop {
  0%   { transform: translateY(0);     opacity: 1; }
  45%  { transform: translateY(-12px); opacity: 0; }
  46%  { transform: translateY(12px);  opacity: 0; }
  100% { transform: translateY(0);     opacity: 1; }
}
@keyframes hp-pop {
  0%   { transform: scale(1); }
  45%  { transform: scale(1.14); }
  100% { transform: scale(1); }
}
@keyframes hp-badge-in {
  0%   { opacity: 0; transform: scale(1.6) rotate(-6deg); }
  60%  { opacity: 1; transform: scale(0.95) rotate(1deg); }
  100% { opacity: 1; transform: none; }
}
@keyframes hp-badge-out {
  from { opacity: 1; transform: none; }
  to   { opacity: 0; transform: scale(0.8) translateY(4px); }
}
@keyframes hp-error-in {
  0%   { opacity: 0; transform: translateY(-8px); }
  30%  { opacity: 1; transform: translateY(0); }
  45%  { transform: translateX(-6px); }
  60%  { transform: translateX(5px); }
  75%  { transform: translateX(-3px); }
  90%  { transform: translateX(2px); }
  100% { opacity: 1; transform: none; }
}
@keyframes hp-indeterminate {
  from { transform: translateX(-100%); }
  to   { transform: translateX(300%); }
}

@media (prefers-reduced-motion: reduce) {
  .hp-root, .hp-root * {
    animation-duration: 0.01ms !important;
    animation-delay: 0s !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
`;

const prefersReducedMotion = () =>
  typeof window !== 'undefined' && !!window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;

const isTouchDevice = () =>
  typeof window !== 'undefined' && !!window.matchMedia?.('(pointer: coarse)').matches;

const PHONE_QUERY = '(max-width: 639px)';

function useIsPhone() {
  const [phone, setPhone] = useState(
    () => typeof window !== 'undefined' && !!window.matchMedia?.(PHONE_QUERY).matches
  );
  useEffect(() => {
    if (!window.matchMedia) return;
    const mq = window.matchMedia(PHONE_QUERY);
    const onChange = () => setPhone(mq.matches);
    onChange();
    mq.addEventListener ? mq.addEventListener('change', onChange) : mq.addListener(onChange);
    return () => {
      mq.removeEventListener ? mq.removeEventListener('change', onChange) : mq.removeListener(onChange);
    };
  }, []);
  return phone;
}

/* Text "decodes" from noise into the real string, left to right. */
function useScramble(target: string, duration = 700) {
  const [text, setText] = useState(target);
  useEffect(() => {
    if (prefersReducedMotion()) {
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
          .map((c, i) => (c === ' ' || c === '/' || i < settled ? c : glyphs[Math.floor(Math.random() * glyphs.length)]))
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

/* Types the placeholder out once, with a block cursor, after the page reveal. */
function useTypewriter(target: string, startDelay = 1100, speed = 26) {
  const [count, setCount] = useState(0);
  useEffect(() => {
    setCount(0);
    if (prefersReducedMotion()) {
      setCount(target.length);
      return;
    }
    let i = 0;
    let t = 0;
    const step = () => {
      i += 1;
      setCount(i);
      if (i < target.length) t = window.setTimeout(step, speed + Math.random() * 30);
    };
    const s = window.setTimeout(step, startDelay);
    return () => {
      window.clearTimeout(s);
      window.clearTimeout(t);
    };
  }, [target, startDelay, speed]);
  return count >= target.length ? target : target.slice(0, count) + (count > 0 ? '\u258C' : '');
}

export const Homepage: React.FC<Props> = ({ onSubmitQuestion, isLoading }) => {
  const [query, setQuery] = useState('');
  const [attachedFile, setAttachedFile] = useState<{ id?: string; name: string } | null>(null);
  const [removing, setRemoving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [selectedField, setSelectedField] = useState<string | null>(null); // kept from original

  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const rootRef = useRef<HTMLElement>(null);
  const dockRef = useRef<HTMLDivElement>(null);
  const removeTimer = useRef<number | undefined>(undefined);

  const isPhone = useIsPhone();
  const label = useScramble('QUERY DESK / NO. 001');
  const typedPlaceholder = useTypewriter(isPhone ? PHONE_PLACEHOLDER : PLACEHOLDER);

  useEffect(() => {
    // Don't auto-focus on touch devices: it pops the keyboard over the page on load
    if (textareaRef.current && !isTouchDevice()) {
      textareaRef.current.focus();
    }
    return () => window.clearTimeout(removeTimer.current);
  }, []);

  // Phone: track the on-screen keyboard so the docked composer rides above it
  useEffect(() => {
    if (!isPhone) return;
    const vv = window.visualViewport;
    const root = rootRef.current;
    if (!vv || !root) return;
    const update = () => {
      const kb = Math.max(0, window.innerHeight - vv.height - vv.offsetTop);
      root.style.setProperty('--hp-kb', `${kb}px`);
      root.dataset.kb = kb > 80 ? 'true' : 'false';
    };
    update();
    vv.addEventListener('resize', update);
    vv.addEventListener('scroll', update);
    return () => {
      vv.removeEventListener('resize', update);
      vv.removeEventListener('scroll', update);
    };
  }, [isPhone]);

  // Phone: reserve room for the docked composer so content never hides behind it
  useEffect(() => {
    if (!isPhone) return;
    const el = dockRef.current;
    const root = rootRef.current;
    if (!el || !root || typeof ResizeObserver === 'undefined') return;
    const ro = new ResizeObserver(() => root.style.setProperty('--hp-dock-h', `${el.offsetHeight}px`));
    ro.observe(el);
    return () => ro.disconnect();
  }, [isPhone]);

  // Phone: textarea grows with its content, up to ~5 lines
  useEffect(() => {
    const ta = textareaRef.current;
    if (!isPhone || !ta) return;
    ta.style.height = 'auto';
    ta.style.height = `${Math.min(ta.scrollHeight, 140)}px`;
  }, [query, isPhone]);

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setQuery(e.target.value);
    setErrorMessage(null);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Desktop: Enter sends, Shift+Enter = newline. Touch: Enter = newline, use the send button.
    if (e.key === 'Enter' && !e.shiftKey && !isTouchDevice()) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const activeDocId = attachedFile && !removing ? attachedFile.id : undefined;

  const handleSubmit = () => {
    const trimmed = query.trim();
    if (!trimmed || isLoading || uploading) return;
    setErrorMessage(null);
    onSubmitQuestion(trimmed, activeDocId);
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setErrorMessage(null);
    try {
      const text = await file.text();
      const doc = await ingestText(file.name, text, `upload://${file.name}`, 'PEER_REVIEWED');
      window.clearTimeout(removeTimer.current);
      setRemoving(false);
      setAttachedFile({ id: doc.id, name: file.name });
    } catch (err: any) {
      setErrorMessage(err.message || 'File upload and text ingestion failed.');
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const removeAttachment = () => {
    setRemoving(true);
    window.clearTimeout(removeTimer.current);
    removeTimer.current = window.setTimeout(() => {
      setAttachedFile(null);
      setRemoving(false);
    }, 200);
  };

  const canSend = !!query.trim() && !isLoading && !uploading;

  const heading = (
    <h1
      className="hp-hero hp-hero-wrap text-[#211E19] font-black tracking-[0.06em] sm:tracking-[0.08em] leading-none mb-3 select-none"
      style={{ fontFamily: 'var(--font-slab)' }}
      aria-label="AXION"
    >
      {'AXION'.split('').map((ch, i) => (
        <span
          key={i}
          aria-hidden
          className="hp-letter inline-block"
          style={{
            animation: `hp-type 700ms ${120 + i * 80}ms ${SPRING} backwards`,
            transition: `transform 340ms ${SPRING}`,
            transitionDelay: `${i * 45}ms`,
          }}
        >
          {ch}
        </span>
      ))}
    </h1>
  );

  const labelEl = (
    <div
      className="font-mono text-[10px] sm:text-[12px] font-bold uppercase tracking-[0.18em] text-[#70695D] mb-1"
      aria-label="QUERY DESK / NO. 001"
    >
      <span aria-hidden>{label}</span>
    </div>
  );

  const fileInput = (
    <input
      ref={fileInputRef}
      type="file"
      accept=".txt,.pdf,.md,.json,.csv"
      onChange={handleFileChange}
      className="hidden"
    />
  );

  const attachmentBadge = attachedFile && (
    <div
      key={attachedFile.id ?? attachedFile.name}
      className={`${removing ? 'hp-badge-out' : 'hp-badge-in'} flex items-center gap-1 px-1.5 sm:px-2 py-0.5 sm:py-1 bg-[#FBF5E6] border-[1.5px] border-[#211E19] text-[10px] sm:text-xs font-mono text-[#211E19] shadow-[1px_1px_0px_#211E19]`}
    >
      <FileText className="w-3 sm:w-3.5 h-3 sm:h-3.5 shrink-0" />
      <span className="max-w-[55vw] sm:max-w-[160px] truncate">{attachedFile.name}</span>
      <button
        type="button"
        onClick={removeAttachment}
        className="hp-x hp-hit hp-hit-x text-[#B83A22] ml-1 p-0.5 font-bold shrink-0"
        title="Remove attachment"
        aria-label="Remove attachment"
      >
        <X className="w-3 h-3" />
      </button>
    </div>
  );

  const errorBox = errorMessage && (
    <div
      key={errorMessage}
      role="alert"
      className="hp-error mt-2 flex items-center gap-2 text-xs font-mono text-[#B83A22] bg-[#FBEBE9] border-[1.5px] border-[#B83A22] p-3 shadow-[2px_2px_0px_#B83A22]"
    >
      <AlertCircle className="w-4 h-4 shrink-0" />
      <span className="min-w-0 break-words">ERROR: {errorMessage}</span>
    </div>
  );

  /* ================================================================== */
  /*  PHONE: chatbot layout                                              */
  /* ================================================================== */
  if (isPhone) {
    const hideChips = !!query.trim() || isLoading;
    return (
      <main
        ref={rootRef}
        className="hp-root hp-phone-root w-full mx-auto flex flex-col items-center justify-center text-center select-text"
      >
        <style>{HOME_CSS}</style>

        {labelEl}
        {heading}

        {/* Suggestion chips: tap to fill the composer */}
        <div className="hp-chips" data-hidden={hideChips}>
          {SUGGESTIONS.map((s, i) => (
            <button
              key={s}
              type="button"
              data-sound="pop"
              className="hp-chip hp-hit font-mono"
              style={{ animation: `hp-chip-in 520ms ${1300 + i * 90}ms ${EXPO} backwards` }}
              onClick={() => {
                setQuery(s);
                setErrorMessage(null);
                textareaRef.current?.focus();
              }}
            >
              {s}
            </button>
          ))}
        </div>

        {/* Docked composer */}
        <div ref={dockRef} className="hp-dock text-left">
          {errorBox}

          {(uploading || attachedFile) && (
            <div className="flex flex-wrap items-center gap-2">
              {uploading && (
                <span className="font-mono text-[11px] text-[#211E19] animate-pulse">[INDEXING...]</span>
              )}
              {attachmentBadge}
            </div>
          )}

          <div className="hp-pill">
            {(uploading || isLoading) && (
              <span
                aria-hidden
                className="hp-bar pointer-events-none absolute top-0 left-0 h-[2px] w-1/3 bg-[#B83A22]"
              />
            )}

            {fileInput}
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading || isLoading}
              className="hp-circle hp-hit hp-btn"
              aria-label="Attach research document or data"
              title="Attach research document or data (.txt, .pdf, .md, .csv, .json)"
            >
              <Paperclip className="w-[18px] h-[18px] stroke-[2.2]" />
            </button>

            <textarea
              ref={textareaRef}
              value={query}
              onChange={handleInput}
              onKeyDown={handleKeyDown}
              disabled={isLoading}
              placeholder={typedPlaceholder}
              aria-label={PLACEHOLDER}
              rows={1}
              className="hp-pill-ta font-mono placeholder:text-[#6E675A]"
            />

            <button
              type="button"
              onClick={handleSubmit}
              disabled={!canSend}
              data-sound="send"
              data-busy={isLoading}
              className={`hp-circle hp-hit hp-send ${canSend ? 'hp-send-on hp-pop' : ''}`}
              aria-label="Send question"
              title="Send question"
            >
              <span className="inline-flex overflow-hidden">
                <ArrowUp className="hp-arrow w-[18px] h-[18px] stroke-[2.5]" data-busy={isLoading} />
              </span>
            </button>
          </div>
        </div>
      </main>
    );
  }

  /* ================================================================== */
  /*  DESKTOP / TABLET (640px and up): original layout                   */
  /* ================================================================== */
  return (
    <main
      ref={rootRef}
      className="hp-root w-full max-w-[780px] mx-auto my-auto flex flex-col justify-center select-text"
    >
      <style>{HOME_CSS}</style>

      {labelEl}
      {heading}

      {/* Main rectangular query editor box: curtain-reveals on load, lifts on focus */}
      <div className="hp-editor hp-reveal w-full bg-[#FBF5E6] border-2 border-[#211E19] shadow-[6px_6px_0px_#211E19] flex flex-col overflow-hidden mb-5">
        {/* Title strip: pinstripes drift while loading, left square spins */}
        <div className="relative h-[28px] bg-[#F3EAD3] border-b-2 border-[#211E19] flex items-center justify-between px-2 select-none overflow-hidden">
          <div className="hp-stripes absolute inset-0 pointer-events-none opacity-80" data-busy={isLoading} />

          <div className="relative z-10 w-[13px] h-[13px] bg-[#FBF5E6] border-[1.5px] border-[#211E19] flex items-center justify-center pointer-events-none">
            <span className="hp-dash w-1.5 h-[1.5px] bg-[#211E19]" data-busy={isLoading} />
          </div>

          <div className="relative z-10 px-2.5 py-0.5 bg-[#FBF5E6] border-[1.5px] border-[#211E19] font-mono text-[10px] font-bold tracking-widest text-[#211E19] uppercase">
            QUERY.TXT
          </div>

          <div className="relative z-10 w-[13px] h-[13px] opacity-0" />
        </div>

        {/* Text area: placeholder types itself out once */}
        <div className="hp-pad p-5 flex-1">
          <textarea
            ref={textareaRef}
            value={query}
            onChange={handleInput}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            placeholder={typedPlaceholder}
            aria-label={PLACEHOLDER}
            rows={3}
            className="hp-textarea w-full h-full resize-none border-none outline-none font-mono text-[#211E19] placeholder:text-[#6E675A] bg-transparent leading-relaxed"
          />
        </div>

        {/* Bottom action strip: ATTACH on left, SEND on right */}
        <div className="relative border-t-2 border-[#211E19] bg-[#F3EAD3] px-3.5 py-2.5 flex items-start justify-between gap-3 select-none">
          {uploading && (
            <span
              aria-hidden
              className="hp-bar pointer-events-none absolute -top-[2px] left-0 h-[2px] w-1/3 bg-[#B83A22]"
            />
          )}

          <div className="flex flex-wrap items-center gap-2.5 min-w-0 flex-1">
            {fileInput}
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading || isLoading}
              className="hp-btn hp-attach hp-hit h-8 px-3 bg-[#FBF5E6] text-[#211E19] border-2 border-[#211E19] shadow-[2px_2px_0px_#211E19] active:translate-x-[1px] active:translate-y-[1px] active:shadow-none flex items-center gap-1 font-mono text-xs font-bold uppercase tracking-wider cursor-pointer disabled:opacity-50 transition-none"
              title="Attach research document or data (.txt, .pdf, .md, .csv, .json)"
            >
              <Paperclip
                className="hp-clip w-3.5 h-3.5 stroke-[2.2]"
                style={{ transition: `transform 380ms ${SPRING}` }}
              />
              <span>ATTACH</span>
            </button>

            {uploading && (
              <span className="font-mono text-xs text-[#211E19] animate-pulse">[INDEXING...]</span>
            )}

            {attachmentBadge}
          </div>

          <button
            type="button"
            onClick={handleSubmit}
            disabled={!canSend}
            data-sound="send"
            className={`hp-hit h-8 px-4 shrink-0 font-mono text-xs font-bold uppercase tracking-wider border-2 border-[#211E19] flex items-center justify-center gap-1 transition-none shadow-[2px_2px_0px_#211E19] ${canSend
                ? 'hp-send-on hp-pop bg-[#B83A22] text-white active:translate-x-[1px] active:translate-y-[1px] active:shadow-none cursor-pointer'
                : 'bg-[#B83A22] text-white opacity-90 cursor-pointer'
              }`}
            title="Submit question to the desk (Enter)"
          >
            <span>SEND</span>
            <span className="inline-flex overflow-hidden">
              <ArrowUp
                className="hp-arrow w-3.5 h-3.5 stroke-[2.5]"
                data-busy={isLoading}
                style={{ transition: `transform 300ms ${SPRING}` }}
              />
            </span>
          </button>
        </div>
      </div>

      {errorBox}
    </main>
  );
};