// AXION — Research Workspace Client Application

let attachedDocumentId = null;
let currentInvestigation = null;

// DOM Elements
const homeView = document.getElementById('home-view');
const loadingView = document.getElementById('loading-view');
const resultsView = document.getElementById('results-view');

const questionInput = document.getElementById('question-input');
const sendBtn = document.getElementById('send-btn');
const attachBtn = document.getElementById('attach-btn');
const fileUpload = document.getElementById('file-upload');
const attachedPill = document.getElementById('attached-pill');
const attachedName = document.getElementById('attached-name');
const removeAttachBtn = document.getElementById('remove-attach-btn');
const newQueryBtn = document.getElementById('new-query-btn');
const brandLink = document.getElementById('brand-link');

const historyToggleBtn = document.getElementById('history-toggle-btn');
const historyDrawer = document.getElementById('history-drawer');
const closeDrawerBtn = document.getElementById('close-drawer-btn');
const historyList = document.getElementById('history-list');

const workspacesBtn = document.getElementById('workspaces-btn');
const workspacesModal = document.getElementById('workspaces-modal');
const closeModalBtn = document.getElementById('close-modal-btn');

const loadingStepText = document.getElementById('loading-step-text');

// Initialize event listeners
document.addEventListener('DOMContentLoaded', () => {
  setupInputListeners();
  setupAttachmentListeners();
  setupNavigationListeners();
  loadHistory();
});

// View Switching Helper
function switchView(viewName) {
  homeView.classList.remove('active');
  loadingView.classList.remove('active');
  resultsView.classList.remove('active');

  if (viewName === 'home') {
    homeView.classList.add('active');
    questionInput.focus();
  } else if (viewName === 'loading') {
    loadingView.classList.add('active');
  } else if (viewName === 'results') {
    resultsView.classList.add('active');
  }
}

// Input Handlers
function setupInputListeners() {
  questionInput.addEventListener('input', () => {
    // Auto-grow textarea
    questionInput.style.height = 'auto';
    questionInput.style.height = Math.min(questionInput.scrollHeight, 180) + 'px';

    const hasText = questionInput.value.trim().length > 0;
    sendBtn.disabled = !hasText;
  });

  // Submit on Enter without Shift
  questionInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!sendBtn.disabled) {
        submitQuestion();
      }
    }
  });

  sendBtn.addEventListener('click', () => {
    if (!sendBtn.disabled) {
      submitQuestion();
    }
  });

  newQueryBtn.addEventListener('click', () => {
    questionInput.value = '';
    questionInput.style.height = 'auto';
    sendBtn.disabled = true;
    switchView('home');
  });

  brandLink.addEventListener('click', (e) => {
    e.preventDefault();
    switchView('home');
  });
}

// File Attachment Handlers
function setupAttachmentListeners() {
  attachBtn.addEventListener('click', () => {
    fileUpload.click();
  });

  fileUpload.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    attachedName.textContent = file.name;
    attachedPill.classList.add('active');

    // Upload file to backend document endpoint
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', file.name);

    try {
      const resp = await fetch('/api/v1/documents/upload', {
        method: 'POST',
        body: formData,
      });
      if (resp.ok) {
        const data = await resp.json();
        attachedDocumentId = data.document_id;
      } else {
        // Fallback: use filename identifier
        attachedDocumentId = 'local-' + Date.now();
      }
    } catch (err) {
      attachedDocumentId = 'local-' + Date.now();
    }
  });

  removeAttachBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    attachedDocumentId = null;
    fileUpload.value = '';
    attachedPill.classList.remove('active');
  });
}

// Navigation & Modal Handlers
function setupNavigationListeners() {
  historyToggleBtn.addEventListener('click', () => {
    historyDrawer.classList.toggle('open');
    loadHistory();
  });

  closeDrawerBtn.addEventListener('click', () => {
    historyDrawer.classList.remove('open');
  });

  workspacesBtn.addEventListener('click', () => {
    workspacesModal.classList.add('open');
  });

  closeModalBtn.addEventListener('click', () => {
    workspacesModal.classList.remove('open');
  });

  workspacesModal.addEventListener('click', (e) => {
    if (e.target === workspacesModal) {
      workspacesModal.classList.remove('open');
    }
  });
}

// Submit Question & Execute Pipeline
async function submitQuestion() {
  const query = questionInput.value.trim();
  if (!query) return;

  switchView('loading');

  // Rotate realistic progress steps during processing
  const steps = [
    "Identifying relevant scientific domains & principles...",
    "Traversing concept graph & verifying dimensional formulas...",
    "Evaluating analogical schema projection & applicability guard...",
    "Executing hypothesis tests & validating findings...",
  ];
  let stepIdx = 0;
  loadingStepText.textContent = steps[0];
  const interval = setInterval(() => {
    stepIdx = (stepIdx + 1) % steps.length;
    loadingStepText.textContent = steps[stepIdx];
  }, 700);

  try {
    const response = await fetch('/api/v1/investigation/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: query,
        document_id: attachedDocumentId,
      }),
    });

    clearInterval(interval);

    if (!response.ok) {
      throw new Error(`Server returned ${response.status}: ${await response.text()}`);
    }

    const data = await response.json();
    currentInvestigation = data;
    renderResults(data);
    saveToLocalHistory(data);
    switchView('results');

  } catch (err) {
    clearInterval(interval);
    alert('Investigation error: ' + err.message);
    switchView('home');
  }
}

// Render Results View
function renderResults(data) {
  document.getElementById('res-question-title').textContent = data.query;

  // Epistemic Tier Badge
  const badge = document.getElementById('res-badge');
  badge.className = 'badge-tier';
  if (data.epistemic_tier.includes('VALIDATED')) {
    badge.classList.add('badge-tier-4');
    badge.textContent = 'Tier 4: Validated Finding';
  } else if (data.epistemic_tier.includes('FACT')) {
    badge.classList.add('badge-tier-1');
    badge.textContent = 'Tier 1: Documented Fact';
  } else {
    badge.classList.add('badge-tier-3');
    badge.textContent = 'Tier 3: Conjectured Hypothesis';
  }

  // Answer Body (Markdown-like formatting)
  const bodyEl = document.getElementById('res-answer-body');
  bodyEl.innerHTML = formatMarkdown(data.answer);

  // Cross-Domain Transfers Accordion
  const transfersAccordion = document.getElementById('accordion-transfers');
  const transfersContent = document.getElementById('transfers-content');
  if (data.transfers && data.transfers.length > 0) {
    transfersAccordion.style.display = 'block';
    document.getElementById('transfers-count').textContent = `(${data.transfers.length})`;
    transfersContent.innerHTML = data.transfers.map(t => `
      <div style="padding: 0.75rem 0; border-bottom: 1px solid var(--border-color);">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
          <span style="font-weight: 600; font-size: 0.875rem;">${escapeHtml(t.source)} &rarr; ${escapeHtml(t.target)}</span>
          <span style="font-weight: 700; font-size: 0.75rem; color: ${t.verdict === 'ACCEPTED' ? 'var(--success-color)' : (t.verdict === 'CONDITIONAL' ? 'var(--warning-color)' : 'var(--danger-color)')};">${t.verdict}</span>
        </div>
        ${t.equation ? `<div style="font-family: var(--font-mono); font-size: 0.8125rem; color: var(--accent-blue); margin-bottom: 0.25rem;">Transferred Equation: ${escapeHtml(t.equation)}</div>` : ''}
        <div style="font-size: 0.8125rem; color: var(--text-secondary);">${escapeHtml(t.rationale)}</div>
      </div>
    `).join('');
  } else {
    transfersAccordion.style.display = 'none';
  }

  // Reasoning Chain Accordion
  const reasoningContent = document.getElementById('reasoning-content');
  reasoningContent.innerHTML = (data.reasoning_steps || []).map(s => `
    <div style="padding: 0.625rem 0; border-bottom: 1px solid #f1f5f9;">
      <span style="font-weight: 600; font-size: 0.8125rem; color: var(--accent-blue);">Step ${s.step}: ${escapeHtml(s.action)}</span>
      <p style="font-size: 0.8125rem; color: var(--text-secondary); margin-top: 0.125rem;">${escapeHtml(s.detail)}</p>
    </div>
  `).join('');

  // Evidence & Provenance Accordion
  const evidenceAccordion = document.getElementById('accordion-evidence');
  const evidenceContent = document.getElementById('evidence-content');
  if (data.evidence_snippets && data.evidence_snippets.length > 0) {
    document.getElementById('evidence-count').textContent = `(${data.evidence_snippets.length})`;
    evidenceContent.innerHTML = data.evidence_snippets.map(e => `
      <div class="evidence-entry">
        <div class="evidence-source">${escapeHtml(e.source)} &bull; ${escapeHtml(e.epistemic_tier)}</div>
        <div class="evidence-text">"${escapeHtml(e.snippet)}"</div>
      </div>
    `).join('');
  } else {
    document.getElementById('evidence-count').textContent = '(0)';
    evidenceContent.innerHTML = '<p style="color: var(--text-muted); padding: 0.5rem 0;">No direct document quotes.</p>';
  }

  // Experiments Accordion
  const expAccordion = document.getElementById('accordion-experiments');
  const expContent = document.getElementById('experiments-content');
  if (data.experiments && data.experiments.length > 0) {
    expAccordion.style.display = 'block';
    expContent.innerHTML = data.experiments.map(exp => `
      <div style="padding: 0.75rem 0; border-bottom: 1px solid var(--border-color);">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
          <span style="font-weight: 600; font-family: var(--font-mono); font-size: 0.8125rem;">Method: ${exp.method}</span>
          <span style="font-weight: 700; font-size: 0.75rem; color: ${exp.verdict === 'SUPPORTED' ? 'var(--success-color)' : 'var(--danger-color)'};">${exp.verdict}</span>
        </div>
        <p style="font-size: 0.8125rem; color: var(--text-secondary);">${escapeHtml(exp.expected_prediction)}</p>
        ${exp.statistical_evidence ? `
          <div style="font-family: var(--font-mono); font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">
            R²: ${exp.statistical_evidence.r_squared} &bull; p-value: ${exp.statistical_evidence.p_value} &bull; RMSE: ${exp.statistical_evidence.rmse}
          </div>
        ` : ''}
      </div>
    `).join('');
  } else {
    expAccordion.style.display = 'none';
  }
}

// Collapsible Accordion Toggle
function toggleAccordion(contentId) {
  const el = document.getElementById(contentId);
  el.classList.toggle('open');
}

// Minimal Markdown Formatter
function formatMarkdown(text) {
  if (!text) return '';
  return text
    .replace(/^### (.*$)/gim, '<h4 style="font-size: 1rem; font-weight: 600; margin: 1rem 0 0.5rem;">$1</h4>')
    .replace(/^## (.*$)/gim, '<h3 style="font-size: 1.125rem; font-weight: 600; margin: 1.25rem 0 0.5rem;">$1</h3>')
    .replace(/^# (.*$)/gim, '<h2 style="font-size: 1.25rem; font-weight: 700; margin: 1.5rem 0 0.75rem;">$1</h2>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n\n/g, '<p></p>')
    .replace(/\n- (.*)/g, '<li>$1</li>');
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// History Management
function saveToLocalHistory(data) {
  let hist = JSON.parse(localStorage.getItem('axion_history') || '[]');
  hist.unshift({
    investigation_id: data.investigation_id,
    query: data.query,
    epistemic_tier: data.epistemic_tier,
    created_at: data.created_at,
    data: data,
  });
  if (hist.length > 25) hist = hist.slice(0, 25);
  localStorage.setItem('axion_history', JSON.stringify(hist));
  loadHistory();
}

async function loadHistory() {
  let hist = JSON.parse(localStorage.getItem('axion_history') || '[]');

  // Also query backend history
  try {
    const res = await fetch('/api/v1/investigation/history');
    if (res.ok) {
      const serverHist = await res.json();
      if (serverHist && serverHist.length > 0) {
        hist = serverHist;
      }
    }
  } catch (e) {
    // Fall back to local storage
  }

  if (hist.length === 0) {
    historyList.innerHTML = '<p style="color: var(--text-muted); font-size: 0.8125rem; padding: 1rem; text-align: center;">No previous investigations.</p>';
    return;
  }

  historyList.innerHTML = hist.map(item => `
    <div class="history-item" onclick="openHistoricalInvestigation('${item.investigation_id}')">
      <div class="history-query">${escapeHtml(item.query)}</div>
      <div class="history-meta">${escapeHtml(item.epistemic_tier || 'Investigated')} &bull; ${new Date(item.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</div>
    </div>
  `).join('');
}

window.openHistoricalInvestigation = async function(invId) {
  historyDrawer.classList.remove('open');
  switchView('loading');

  try {
    const res = await fetch(`/api/v1/investigation/${invId}`);
    if (res.ok) {
      const data = await res.json();
      renderResults(data);
      switchView('results');
      return;
    }
  } catch (e) {}

  // Check local storage fallback
  const hist = JSON.parse(localStorage.getItem('axion_history') || '[]');
  const match = hist.find(h => h.investigation_id === invId);
  if (match && match.data) {
    renderResults(match.data);
    switchView('results');
  } else {
    alert('Investigation not found in cache.');
    switchView('home');
  }
};
