// AXION Retro Mechanical Sound Engine (Web Audio API)
// Zero external files, zero latency, offline & PWA ready.

export type SoundVariant = 'mechanical' | 'switch' | 'send' | 'pop';

let audioCtx: AudioContext | null = null;
let isMuted = false;

function getAudioContext(): AudioContext | null {
  if (typeof window === 'undefined') return null;
  if (!audioCtx) {
    const AudioContextClass =
      window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
    if (AudioContextClass) {
      audioCtx = new AudioContextClass();
    }
  }
  if (audioCtx && audioCtx.state === 'suspended') {
    audioCtx.resume().catch(() => {});
  }
  return audioCtx;
}

/**
 * Play a synthesized retro mechanical click sound.
 */
export function playClickSound(variant: SoundVariant = 'mechanical'): void {
  if (isMuted) return;

  try {
    const ctx = getAudioContext();
    if (!ctx) return;

    const t = ctx.currentTime;

    if (variant === 'switch') {
      // Crisp vintage toggle switch snap
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = 'triangle';
      osc.frequency.setValueAtTime(1400, t);
      osc.frequency.exponentialRampToValueAtTime(120, t + 0.028);

      gain.gain.setValueAtTime(0.22, t);
      gain.gain.exponentialRampToValueAtTime(0.001, t + 0.028);

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start(t);
      osc.stop(t + 0.028);

    } else if (variant === 'send') {
      // Tactile solenoid relay engagement
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = 'sine';
      osc.frequency.setValueAtTime(750, t);
      osc.frequency.exponentialRampToValueAtTime(60, t + 0.045);

      gain.gain.setValueAtTime(0.3, t);
      gain.gain.exponentialRampToValueAtTime(0.001, t + 0.045);

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start(t);
      osc.stop(t + 0.045);

    } else if (variant === 'pop') {
      // Soft chip / suggestion pill tap
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = 'sine';
      osc.frequency.setValueAtTime(600, t);
      osc.frequency.exponentialRampToValueAtTime(300, t + 0.02);

      gain.gain.setValueAtTime(0.12, t);
      gain.gain.exponentialRampToValueAtTime(0.001, t + 0.02);

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start(t);
      osc.stop(t + 0.02);

    } else {
      // Authentic tactile keyboard click: sharp micro-burst noise + body resonance
      const bufferSize = Math.max(1, Math.floor(ctx.sampleRate * 0.012)); // 12ms burst
      const noiseBuffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
      const output = noiseBuffer.getChannelData(0);
      for (let i = 0; i < bufferSize; i++) {
        output[i] = (Math.random() * 2 - 1) * Math.exp(-i / (bufferSize * 0.28));
      }

      const noise = ctx.createBufferSource();
      noise.buffer = noiseBuffer;

      const filter = ctx.createBiquadFilter();
      filter.type = 'bandpass';
      filter.frequency.value = 2600;
      filter.Q.value = 3.5;

      const noiseGain = ctx.createGain();
      noiseGain.gain.setValueAtTime(0.2, t);
      noiseGain.gain.exponentialRampToValueAtTime(0.001, t + 0.012);

      noise.connect(filter);
      filter.connect(noiseGain);
      noiseGain.connect(ctx.destination);

      noise.start(t);
      noise.stop(t + 0.012);

      // Resonant keycap acoustic click
      const osc = ctx.createOscillator();
      const oscGain = ctx.createGain();

      osc.type = 'sine';
      osc.frequency.setValueAtTime(1600, t);
      osc.frequency.exponentialRampToValueAtTime(180, t + 0.015);

      oscGain.gain.setValueAtTime(0.16, t);
      oscGain.gain.exponentialRampToValueAtTime(0.001, t + 0.015);

      osc.connect(oscGain);
      oscGain.connect(ctx.destination);

      osc.start(t);
      osc.stop(t + 0.015);
    }
  } catch {
    // Autoplay restrictions or unsupported device
  }
}

/**
 * Global delegated click listener.
 * Automatically gives every button, link, and switch in AXION tactile audio feedback.
 */
export function initGlobalClickSound(): () => void {
  if (typeof window === 'undefined') return () => {};

  const handlePointerDown = (e: MouseEvent | TouchEvent) => {
    // Resume audio context on first user gesture
    if (audioCtx && audioCtx.state === 'suspended') {
      audioCtx.resume().catch(() => {});
    }

    const target = (e.target as HTMLElement | null)?.closest(
      'button, [role="button"], [role="switch"], a, [data-sound]'
    ) as HTMLElement | null;

    if (!target) return;

    const customSound = target.getAttribute('data-sound') as SoundVariant | 'none' | null;
    if (customSound === 'none') return;

    if (customSound && ['mechanical', 'switch', 'send', 'pop'].includes(customSound)) {
      playClickSound(customSound as SoundVariant);
    } else if (target.getAttribute('role') === 'switch') {
      playClickSound('switch');
    } else if (target.getAttribute('type') === 'submit' || target.textContent?.trim().toUpperCase().includes('SEND')) {
      playClickSound('send');
    } else {
      playClickSound('mechanical');
    }
  };

  window.addEventListener('pointerdown', handlePointerDown, { passive: true, capture: true });

  return () => {
    window.removeEventListener('pointerdown', handlePointerDown, { capture: true });
  };
}

export function setMuted(muted: boolean): void {
  isMuted = muted;
}

export function getMuted(): boolean {
  return isMuted;
}
