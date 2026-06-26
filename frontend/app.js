/* ════════════════════════════════════════════════════════════
   Football AI Management System — Frontend JavaScript
   ════════════════════════════════════════════════════════════ */

'use strict';

// ── Agent display config ───────────────────────────────────────────────────────
const AGENT_CONFIG = {
  planner:       { icon: '🧠', label: 'Planner',   pipeId: 'pipe-planner' },
  financial:     { icon: '💰', label: 'Financial', pipeId: 'pipe-financial' },
  scouter:       { icon: '🔍', label: 'Scouter',   pipeId: 'pipe-scouter' },
  analysis:      { icon: '📊', label: 'Analysis',  pipeId: 'pipe-analysis' },
  tactical:      { icon: '⚔️', label: 'Tactical',  pipeId: 'pipe-tactical' },
  email:         { icon: '✉️', label: 'Email',     pipeId: 'pipe-email' },
  pdf_generator: { icon: '📄', label: 'PDF',       pipeId: 'pipe-pdf' },
};

// ── State ─────────────────────────────────────────────────────────────────────
let currentRunId = null;
let eventSource  = null;

// ── UI Helpers ────────────────────────────────────────────────────────────────

function setQuery(btn) {
  document.getElementById('queryInput').value = btn.textContent.trim();
}

function formatTime(ts) {
  return new Date(ts * 1000).toLocaleTimeString('en-GB', {
    hour: '2-digit', minute: '2-digit', second: '2-digit'
  });
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.appendChild(document.createTextNode(String(str)));
  return div.innerHTML;
}

function formatWage(eur) {
  if (!eur) return '—';
  return '€' + Number(eur).toLocaleString() + '/wk';
}

function clearActivity() {
  const feed = document.getElementById('activityFeed');
  feed.innerHTML = `
    <div class="feed-placeholder">
      <div class="feed-placeholder-icon">🤖</div>
      <div class="feed-placeholder-text">Run a scouting query to see the agents in action</div>
    </div>`;
  document.getElementById('downloadPanel').style.display = 'none';
  document.getElementById('clearBtn').style.display = 'none';
  document.getElementById('runIdDisplay').style.display = 'none';
  currentRunId = null;

  // Reset all pipeline agents
  Object.values(AGENT_CONFIG).forEach(cfg => {
    const el = document.getElementById(cfg.pipeId);
    if (el) el.className = el.className.replace(/\b(active|done|error)\b/g, '').trim();
  });
}

// ── Feed Event Renderer ───────────────────────────────────────────────────────

function renderEvent(event) {
  const feed = document.getElementById('activityFeed');

  // Remove placeholder if still there
  const placeholder = feed.querySelector('.feed-placeholder');
  if (placeholder) placeholder.remove();

  const agent = event.agent || 'system';
  const cfg   = AGENT_CONFIG[agent] || { icon: '🤖', label: agent };
  const type  = event.type || 'progress';

  const badgeClass = {
    agent_start:             'badge-start',
    progress:                'badge-progress',
    agent_complete:          'badge-complete',
    error:                   'badge-error',
    connected:               'badge-system',
    pipeline_complete:       'badge-complete',
    pipeline_error:          'badge-error',
    stream_end:              'badge-system',
    human_decision_required: 'badge-decision',
    player_selection_required:'badge-selection',
    email_draft_ready:       'badge-email',
    pipeline_stopped:        'badge-stopped',
    email_sent:              'badge-complete',
  }[type] || 'badge-progress';

  const badgeLabel = {
    agent_start:             'Starting',
    progress:                'Running',
    agent_complete:          'Done ✓',
    error:                   'Error',
    connected:               'Connected',
    pipeline_complete:       'Complete ✓',
    pipeline_error:          'Failed',
    stream_end:              'Stream End',
    human_decision_required: 'Awaiting Decision',
    player_selection_required:'Select Player',
    email_draft_ready:       'Email Ready',
    pipeline_stopped:        'Stopped',
    email_sent:              'Email Sent ✓',
  }[type] || type;

  // Format optional data preview
  let dataHtml = '';
  if (event.data && typeof event.data === 'object') {
    const preview = JSON.stringify(event.data, null, 2);
    if (preview.length < 2000) {
      dataHtml = `<div class="event-data">${escapeHtml(preview)}</div>`;
    }
  } else if (event.error) {
    dataHtml = `<div class="event-data" style="color: var(--red);">${escapeHtml(event.error)}</div>`;
  }

  const ts = event.timestamp ? formatTime(event.timestamp) : new Date().toLocaleTimeString();

  const el = document.createElement('div');
  el.className = 'feed-event';
  el.innerHTML = `
    <div class="event-agent-icon">${cfg.icon}</div>
    <div class="event-body">
      <div class="event-header">
        <span class="event-agent-name">${cfg.label || agent}</span>
        <span class="event-type-badge ${badgeClass}">${badgeLabel}</span>
        <span class="event-timestamp">${ts}</span>
      </div>
      <div class="event-message">${escapeHtml(event.message || '')}</div>
      ${dataHtml}
    </div>`;

  feed.appendChild(el);
  feed.scrollTop = feed.scrollHeight;
}

// ── HITL: Decision Card ───────────────────────────────────────────────────────

function renderDecisionCard(event) {
  const feed = document.getElementById('activityFeed');
  const placeholder = feed.querySelector('.feed-placeholder');
  if (placeholder) placeholder.remove();

  const agent   = event.agent || 'system';
  const cfg     = AGENT_CONFIG[agent] || { icon: '🤖', label: agent };
  const data    = event.data || {};
  const summary = JSON.stringify(data, null, 2);
  const cardId  = `decision-${agent}-${currentRunId}`;

  // Reuse existing card for adjustment re-runs (update in place)
  let card = document.getElementById(cardId);
  const isUpdate = !!card;

  if (!card) {
    card = document.createElement('div');
    card.className = 'decision-card';
    card.id = cardId;
  } else {
    card.classList.remove('adjusting', 'resolved');
  }

  card.innerHTML = `
    <div class="decision-header">
      <span class="decision-agent-icon">${cfg.icon}</span>
      <span>${cfg.label} agent output — review and decide</span>
      ${isUpdate ? '<span class="decision-updated-badge">Updated</span>' : ''}
    </div>
    <div class="decision-summary">${escapeHtml(summary)}</div>
    <div class="adjustment-section">
      <textarea
        class="adjustment-textarea"
        id="adj-${agent}-${currentRunId}"
        placeholder="Optional: describe an adjustment (e.g. 'set value_max to 50,000,000') — leave blank to just proceed"
        rows="2"
      ></textarea>
      <div class="adjustment-hint">Leave blank and click Proceed, or type a change and click Proceed to re-run with that adjustment</div>
    </div>
    <div class="decision-actions">
      <button class="btn-proceed" onclick="handleProceed('${agent}')">✓ Proceed</button>
      <button class="btn-stop"    onclick="handleStop('${agent}')">✕ Stop</button>
    </div>`;

  if (!isUpdate) {
    feed.appendChild(card);
  }
  feed.scrollTop = feed.scrollHeight;
}

function handleProceed(agentName) {
  if (!currentRunId) return;
  const textarea = document.getElementById(`adj-${agentName}-${currentRunId}`);
  const comment  = textarea ? textarea.value.trim() : '';
  const card     = document.getElementById(`decision-${agentName}-${currentRunId}`);

  if (comment) {
    // Has adjustment text → re-run agent with adjustment, show loading state
    if (card) {
      card.classList.add('adjusting');
      const actions = card.querySelector('.decision-actions');
      if (actions) actions.innerHTML = '<div class="adjusting-indicator">⟳ Re-running with your adjustment...</div>';
    }
    sendDecision('adjust', comment);
  } else {
    // No text → proceed to next agent
    if (card) card.classList.add('resolved');
    sendDecision('proceed', '');
  }
}

function handleStop(agentName) {
  if (!currentRunId) return;
  document.querySelectorAll('.decision-card').forEach(c => c.classList.add('resolved'));
  sendDecision('stop', '');
}

function sendDecision(action, comment) {
  if (!currentRunId) return;
  fetch(`/api/scout/${currentRunId}/decision`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action, comment: comment || '' }),
  }).catch(console.error);
}

// ── Player Selection Cards ────────────────────────────────────────────────────

function renderPlayerSelectionCards(event) {
  const feed = document.getElementById('activityFeed');
  const placeholder = feed.querySelector('.feed-placeholder');
  if (placeholder) placeholder.remove();

  const players = (event.data && event.data.players) || [];

  const wrapper = document.createElement('div');
  wrapper.className = 'player-selection-wrapper';
  wrapper.id = `player-selection-${currentRunId}`;

  const cardsHtml = players.map((p, i) => {
    const rank = p.rank || (i + 1);
    const rankClass = rank === 1 ? 'rank-1' : rank === 2 ? 'rank-2' : 'rank-3';
    const rankLabel = rank === 1 ? '#1 Best Match' : rank === 2 ? '#2 Runner-up' : '#3 Alternative';
    const score = p.tactical_fit_score || 0;
    const fitClass = score >= 70 ? 'fit-high' : score >= 50 ? 'fit-mid' : 'fit-low';
    const strengths = (p.strengths || []).slice(0, 2);
    const strengthTags = strengths.map(s => `<span class="strength-tag">${escapeHtml(s)}</span>`).join('');

    return `
      <div class="player-card" onclick="sendPlayerSelection('${escapeHtml(p.name)}', this)">
        <div class="player-rank-badge ${rankClass}">${rankLabel}</div>
        <div class="player-card-name">${escapeHtml(p.name)}</div>
        <div class="player-card-meta">${escapeHtml(p.position || '')} · Age ${p.age || '?'} · ${escapeHtml(p.club || '')}</div>
        <div class="player-card-wage">${formatWage(p.wage_eur)}</div>
        <div class="player-fit-row">
          <span class="player-fit-label">Tactical Fit:</span>
          <span class="player-fit-score ${fitClass}">${score}</span>
          <span class="player-fit-label">/ 100</span>
        </div>
        ${strengthTags ? `<div class="player-strengths">${strengthTags}</div>` : ''}
      </div>`;
  }).join('');

  wrapper.innerHTML = `
    <div class="player-selection-label">⚽ Select a player to send a recruitment offer:</div>
    <div class="player-cards-row">${cardsHtml}</div>
    <div class="select-player-hint">Click a card to select the player — the pipeline will continue with your choice</div>`;

  feed.appendChild(wrapper);
  feed.scrollTop = feed.scrollHeight;
}

function sendPlayerSelection(playerName, cardEl) {
  if (!currentRunId) return;

  // Visual feedback: highlight selected, dim others
  const wrapper = document.getElementById(`player-selection-${currentRunId}`);
  if (wrapper) {
    wrapper.querySelectorAll('.player-card').forEach(c => {
      c.classList.add(c === cardEl ? 'selected' : 'dimmed');
    });
    const hint = wrapper.querySelector('.select-player-hint');
    if (hint) hint.textContent = `Selected: ${playerName} — continuing pipeline...`;
  }

  fetch(`/api/scout/${currentRunId}/select-player`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ player_name: playerName }),
  }).catch(console.error);
}

// ── Email Preview Card ────────────────────────────────────────────────────────

function renderEmailPreview(event) {
  const feed = document.getElementById('activityFeed');
  const placeholder = feed.querySelector('.feed-placeholder');
  if (placeholder) placeholder.remove();

  const data = event.data || {};
  const draft   = data.draft   || '';
  const subject = data.subject || '';
  const to      = data.to      || '';
  const from    = data.from    || '';

  const card = document.createElement('div');
  card.className = 'email-preview-card';
  card.id = `email-preview-${currentRunId}`;
  card.innerHTML = `
    <div class="email-preview-header">
      <span>✉️</span>
      <span>Recruitment Email Draft — Review &amp; Send</span>
    </div>
    <div class="email-meta">
      <div>From: <span>${escapeHtml(from)}</span></div>
      <div>To: <span>${escapeHtml(to)}</span></div>
    </div>
    <div class="email-subject-row">
      <span class="email-subject-label">Subject</span>
      ${escapeHtml(subject)}
    </div>
    <textarea class="email-body-editor" id="email-body-${currentRunId}">${escapeHtml(draft)}</textarea>
    <div class="email-actions">
      <button class="btn-send-email" onclick="sendEmail(this)">Send Email ✉️</button>
      <span class="email-hint">You can edit the draft above before sending</span>
    </div>`;

  feed.appendChild(card);
  feed.scrollTop = feed.scrollHeight;
}

function sendEmail(btn) {
  if (!currentRunId) return;

  const textarea = document.getElementById(`email-body-${currentRunId}`);
  const body = textarea ? textarea.value : '';

  const card = document.getElementById(`email-preview-${currentRunId}`);
  if (card) {
    card.classList.add('sent');
    btn.textContent = 'Sending...';
  }

  fetch(`/api/scout/${currentRunId}/send-email`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email_body: body }),
  }).catch(console.error);
}

// ── Pipeline Status Updater ───────────────────────────────────────────────────

function updatePipelineAgent(agentName, status) {
  const cfg = AGENT_CONFIG[agentName];
  if (!cfg?.pipeId) return;
  const el = document.getElementById(cfg.pipeId);
  if (!el) return;

  el.classList.remove('active', 'done', 'error');
  if (status) el.classList.add(status);
}

// ── Main Scouting Function ────────────────────────────────────────────────────

async function startScouting() {
  const query = document.getElementById('queryInput').value.trim();
  if (!query) {
    document.getElementById('queryInput').focus();
    return;
  }

  // Close any existing stream
  if (eventSource) {
    eventSource.close();
    eventSource = null;
  }

  // UI reset & loading state
  clearActivity();
  const scoutBtn = document.getElementById('scoutBtn');
  scoutBtn.disabled = true;
  scoutBtn.classList.add('running');
  scoutBtn.querySelector('.btn-icon').textContent = '⏳';
  scoutBtn.querySelector('.btn-text').textContent = 'Pipeline Running...';

  document.getElementById('clearBtn').style.display = 'inline-flex';

  let response;
  try {
    response = await fetch('/api/scout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });
  } catch (err) {
    renderEvent({
      type: 'error', agent: 'system',
      message: `Failed to connect to API: ${err.message}`,
      timestamp: Date.now() / 1000,
    });
    resetScoutBtn();
    return;
  }

  if (!response.ok) {
    renderEvent({
      type: 'error', agent: 'system',
      message: `API error ${response.status}: ${response.statusText}`,
      timestamp: Date.now() / 1000,
    });
    resetScoutBtn();
    return;
  }

  // Read SSE stream
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  const processStream = async () => {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop();

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        const jsonStr = line.slice(6).trim();
        if (!jsonStr) continue;

        let event;
        try { event = JSON.parse(jsonStr); }
        catch { continue; }

        handleEvent(event);
      }
    }
    resetScoutBtn();
  };

  processStream().catch(err => {
    renderEvent({
      type: 'error', agent: 'system',
      message: `Stream error: ${err.message}`,
      timestamp: Date.now() / 1000,
    });
    resetScoutBtn();
  });
}

// ── Event Handler ─────────────────────────────────────────────────────────────

function handleEvent(event) {
  const type = event.type;

  // Capture run ID on first event
  if (event.run_id && !currentRunId) {
    currentRunId = event.run_id;
    const runDisplay = document.getElementById('runIdDisplay');
    runDisplay.textContent = `Run: ${event.run_id.slice(0, 8)}`;
    runDisplay.style.display = 'inline-flex';
  }

  // Update pipeline agent status
  if (event.agent && type === 'agent_start') {
    updatePipelineAgent(event.agent, 'active');
  } else if (event.agent && type === 'agent_complete') {
    updatePipelineAgent(event.agent, 'done');
  } else if (event.agent && (type === 'error' || type === 'pipeline_stopped')) {
    updatePipelineAgent(event.agent, 'error');
  }

  // Intercept special interactive event types — render custom UI instead of generic feed item
  if (type === 'human_decision_required') {
    renderDecisionCard(event);
    return;
  }
  if (type === 'player_selection_required') {
    renderPlayerSelectionCards(event);
    return;
  }
  if (type === 'email_draft_ready') {
    updatePipelineAgent('email', 'active');
    renderEmailPreview(event);
    return;
  }
  if (type === 'email_sent') {
    updatePipelineAgent('email', 'done');
    // fall through to renderEvent for the confirmation message
  }

  // Generic feed item
  renderEvent(event);

  // Pipeline complete → show download panel
  if (type === 'pipeline_complete' && event.run_id) {
    showDownloadPanel(event);
  }

  // Stream end / timeout → re-enable button
  if (type === 'stream_end' || type === 'timeout') {
    resetScoutBtn();
  }
}

// ── Download Panel ────────────────────────────────────────────────────────────

function showDownloadPanel(event) {
  const panel = document.getElementById('downloadPanel');
  const btn   = document.getElementById('downloadBtn');
  const sub   = document.getElementById('downloadSubtitle');

  btn.href = `/api/download/${event.run_id}`;
  sub.textContent = `${event.ranked_count || '3+'} players ranked · Scouting report with charts and tactical analysis ready.`;
  panel.style.display = 'flex';
  panel.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// ── Reset Button ──────────────────────────────────────────────────────────────

function resetScoutBtn() {
  const scoutBtn = document.getElementById('scoutBtn');
  scoutBtn.disabled = false;
  scoutBtn.classList.remove('running');
  scoutBtn.querySelector('.btn-icon').textContent = '🚀';
  scoutBtn.querySelector('.btn-text').textContent = 'Run Scouting Pipeline';
}

// ── Keyboard Shortcut: Ctrl+Enter to submit ───────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('queryInput').addEventListener('keydown', e => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      startScouting();
    }
  });
});
