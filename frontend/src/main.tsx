import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

// Register AXION Progressive Web App Service Worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    const rawBase = import.meta.env.BASE_URL || '/';
    const baseWithSlash = rawBase.endsWith('/') ? rawBase : `${rawBase}/`;
    const swUrl = `${baseWithSlash}sw.js`;

    navigator.serviceWorker
      .register(swUrl, { scope: baseWithSlash })
      .then((reg) => {
        console.log('[AXION PWA] Service Worker registered! Scope:', reg.scope);
      })
      .catch((err) => {
        console.warn('[AXION PWA] Service Worker registration failed:', err);
      });
  });
}
