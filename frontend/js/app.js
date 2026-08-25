/**
 * ThreatByte — Dynamic Application Logic & Feed Manager
 */

// Application State
const state = {
  currentPayload: null,
  allArticles: [],
  filteredArticles: [],
  selectedCategory: 'ALL',
  selectedSeverity: 'ALL',
  searchQuery: '',
  archiveList: []
};

// DOM References
const elements = {
  briefingDateSelect: document.getElementById('briefing-date-select'),
  heroEditionDate: document.getElementById('hero-edition-date'),
  heroThreatStatus: document.getElementById('hero-threat-status'),
  heroTitle: document.getElementById('lead-hero-title'),
  heroSummary: document.getElementById('lead-hero-summary'),
  statTotal: document.getElementById('stat-total-incidents'),
  statCritical: document.getElementById('stat-critical-threats'),
  statCves: document.getElementById('stat-unique-cves'),
  statAiModel: document.getElementById('stat-ai-model'),
  categoryPills: document.getElementById('category-pills-container'),
  severityFilters: document.getElementById('severity-filters-container'),
  searchInput: document.getElementById('search-input'),
  clearSearchBtn: document.getElementById('clear-search-btn'),
  resultsCountText: document.getElementById('results-count-text'),
  feedGeneratedTime: document.getElementById('feed-generated-time'),
  cardsGrid: document.getElementById('threat-cards-grid'),
  btnCopyBriefing: document.getElementById('btn-copy-briefing'),
  toastContainer: document.getElementById('toast-container'),
  modal: document.getElementById('incident-modal'),
  modalBody: document.getElementById('modal-body-content'),
  modalCloseBtn: document.getElementById('modal-close-btn'),
  modalSevBadge: document.getElementById('modal-sev-badge'),
  modalCategory: document.getElementById('modal-category'),
  modalSourceLink: document.getElementById('modal-source-link'),
  modalCopyBtn: document.getElementById('modal-copy-btn')
};

// Initialize Application
document.addEventListener('DOMContentLoaded', async () => {
  setupEventListeners();
  await loadArchiveIndex();
  await loadBriefingData('latest');
});

/**
 * Load archive index to populate historical date dropdown
 */
async function loadArchiveIndex() {
  try {
    const res = await fetch('../data/archive.json');
    if (res.ok) {
      const data = await res.json();
      state.archiveList = data;
      populateDateSelector(data);
    }
  } catch (err) {
    console.warn("Archive index not available, running in single edition mode.");
  }
}

function populateDateSelector(archives) {
  elements.briefingDateSelect.innerHTML = '<option value="latest">Latest Edition (Live)</option>';
  archives.forEach(item => {
    const opt = document.createElement('option');
    opt.value = item.date;
    opt.textContent = `${item.date} (${item.total_incidents} stories)`;
    elements.briefingDateSelect.appendChild(opt);
  });
}

/**
 * Load daily briefing payload
 */
async function loadBriefingData(targetDate = 'latest') {
  elements.cardsGrid.innerHTML = `
    <div class="feed-loading">
      <div class="editorial-spinner"></div>
      <p>Loading curated threat intelligence dispatch...</p>
    </div>
  `;

  let payload = null;
  const path = targetDate === 'latest' ? '../data/latest.json' : `../data/daily/${targetDate}.json`;

  try {
    const res = await fetch(path);
    if (res.ok) {
      payload = await res.json();
    } else {
      throw new Error(`HTTP ${res.status}`);
    }
  } catch (err) {
    console.warn(`Failed to fetch ${path}, retrying with root fallback:`, err);
    try {
      const altRes = await fetch('data/latest.json');
      if (altRes.ok) payload = await altRes.json();
    } catch (e) {}
  }

  if (!payload) {
    elements.cardsGrid.innerHTML = `
      <div class="feed-empty">
        <h3>Could not load intelligence feed</h3>
        <p>Please check your local web server or generate data using <code>python backend/generator.py</code>.</p>
      </div>
    `;
    return;
  }

  state.currentPayload = payload;
  state.allArticles = payload.articles || [];
  
  updateDashboardHeader(payload);
  applyFilters();
}

/**
 * Update Header and Lead Story
 */
function updateDashboardHeader(payload) {
  const metrics = payload.metrics || {};
  const dateStr = payload.date || 'Today';

  elements.heroEditionDate.textContent = `${dateStr} Edition`;
  elements.heroThreatStatus.textContent = `Threat Status: ${metrics.threat_badge || 'ACTIVE TELEMETRY'}`;

  // Animate stats
  elements.statTotal.textContent = metrics.total_incidents || state.allArticles.length;
  elements.statCritical.textContent = metrics.critical_threats || 0;
  elements.statCves.textContent = metrics.unique_cves_count || 0;

  // Lead Hero Article
  if (state.allArticles.length > 0) {
    const lead = state.allArticles[0];
    elements.heroTitle.textContent = lead.title;
    elements.heroSummary.textContent = lead.executive_summary || '';
  }

  elements.feedGeneratedTime.textContent = `Updated: ${payload.generated_at || dateStr}`;
}

/**
 * Filter & Search Event Listeners
 */
function setupEventListeners() {
  // Date Selector
  elements.briefingDateSelect.addEventListener('change', (e) => {
    loadBriefingData(e.target.value);
  });

  // Category Pills
  elements.categoryPills.addEventListener('click', (e) => {
    const button = e.target.closest('.pill');
    if (!button) return;
    elements.categoryPills.querySelectorAll('.pill').forEach(p => p.classList.remove('active'));
    button.classList.add('active');
    state.selectedCategory = button.getAttribute('data-category');
    applyFilters();
  });

  // Severity Buttons
  elements.severityFilters.addEventListener('click', (e) => {
    const button = e.target.closest('.sev-btn');
    if (!button) return;
    elements.severityFilters.querySelectorAll('.sev-btn').forEach(p => p.classList.remove('active'));
    button.classList.add('active');
    state.selectedSeverity = button.getAttribute('data-severity');
    applyFilters();
  });

  // Search Input
  let debounceTimer;
  elements.searchInput.addEventListener('input', (e) => {
    clearTimeout(debounceTimer);
    state.searchQuery = e.target.value.trim().toLowerCase();
    elements.clearSearchBtn.classList.toggle('hidden', state.searchQuery.length === 0);
    debounceTimer = setTimeout(applyFilters, 120);
  });

  elements.clearSearchBtn.addEventListener('click', () => {
    elements.searchInput.value = '';
    state.searchQuery = '';
    elements.clearSearchBtn.classList.add('hidden');
    applyFilters();
  });

  // Copy Briefing Button
  elements.btnCopyBriefing.addEventListener('click', copyFullBriefingToClipboard);

  // Modal Handlers
  elements.modalCloseBtn.addEventListener('click', closeModal);
  elements.modal.addEventListener('click', (e) => {
    if (e.target === elements.modal) closeModal();
  });
}

function applyFilters() {
  const query = state.searchQuery;
  const category = state.selectedCategory;
  const severity = state.selectedSeverity;

  state.filteredArticles = state.allArticles.filter(art => {
    if (category !== 'ALL' && art.threat_category !== category) {
      return false;
    }
    if (severity !== 'ALL' && art.severity !== severity) {
      return false;
    }
    if (query) {
      const matchTitle = (art.title || '').toLowerCase().includes(query);
      const matchSummary = (art.executive_summary || '').toLowerCase().includes(query);
      const matchCve = (art.cve_ids || []).some(c => c.toLowerCase().includes(query));
      const matchVendor = (art.affected_vendors || []).some(v => v.toLowerCase().includes(query));
      const matchActor = (art.threat_actor || '').toLowerCase().includes(query);
      if (!matchTitle && !matchSummary && !matchCve && !matchVendor && !matchActor) {
        return false;
      }
    }
    return true;
  });

  renderFeedGrid();
  elements.resultsCountText.textContent = `Showing ${state.filteredArticles.length} of ${state.allArticles.length} curated stories`;
}

/**
 * Render Feed Grid
 */
function renderFeedGrid() {
  if (state.filteredArticles.length === 0) {
    elements.cardsGrid.innerHTML = `
      <div class="feed-empty">
        <i class="fa-solid fa-file-circle-question" style="font-size: 28px; margin-bottom: 10px;"></i>
        <h3>No intelligence items match your current filter</h3>
        <p>Try searching for a different keyword or selecting "All Topics".</p>
      </div>
    `;
    return;
  }

  elements.cardsGrid.innerHTML = state.filteredArticles.map((art, idx) => {
    const sev = art.severity || 'MEDIUM';
    const score = art.severity_score || (sev === 'CRITICAL' ? 9.5 : sev === 'HIGH' ? 8.2 : 6.0);
    const scorePercent = Math.min(100, Math.round((score / 10) * 100));

    const cvesHtml = (art.cve_ids || []).map(cve => `
      <span class="cve-badge" onclick="filterByCve('${escapeHtml(cve)}')">
        <i class="fa-solid fa-bug"></i> ${escapeHtml(cve)}
      </span>
    `).join('');

    const vendorsHtml = (art.affected_vendors || []).map(v => `
      <span class="vendor-tag"><i class="fa-solid fa-layer-group"></i> ${escapeHtml(v)}</span>
    `).join('');

    const mitigationsHtml = (art.actionable_mitigations || []).map(m => `
      <li>${escapeHtml(m)}</li>
    `).join('');

    const timeAgo = formatTimeAgo(art.published_at);

    return `
      <article class="article-card">
        <div>
          <div class="article-meta-top">
            <div class="meta-tags-left">
              <span class="tag-severity ${sev}">${sev}</span>
              <span class="tag-category">${escapeHtml(art.threat_category || 'Security')}</span>
            </div>
            <div class="meta-source-time">
              <span>${escapeHtml(art.source || 'CTI Feed')}</span> &bull; <span>${timeAgo}</span>
            </div>
          </div>

          <h3 class="article-title" onclick="openDetailModal(${idx})">
            ${escapeHtml(art.title)}
          </h3>

          <div class="article-cvss-bar-row">
            <div class="cvss-label">CVSS Impact: <strong>${score}/10</strong></div>
            <div class="cvss-progress-track">
              <div class="cvss-progress-fill ${sev}" style="width: ${scorePercent}%;"></div>
            </div>
          </div>

          ${cvesHtml || vendorsHtml ? `
            <div class="cve-vendor-row">
              ${cvesHtml}
              ${vendorsHtml}
            </div>
          ` : ''}

          <p class="article-summary">
            ${escapeHtml(art.executive_summary || '')}
          </p>

          <div class="article-accordion">
            <button class="accordion-btn" onclick="toggleAccordion(this)">
              <span><i class="fa-solid fa-shield-halved"></i> Technical Breakdown & Defense</span>
              <i class="fa-solid fa-chevron-down"></i>
            </button>
            <div class="accordion-body">
              <p><strong>Root Cause & Vector:</strong> ${escapeHtml(art.technical_breakdown || 'Telemetry developing.')}</p>
              ${art.threat_actor && art.threat_actor !== 'Unknown' ? `<p style="margin-top: 6px;"><strong>Attributed Actor:</strong> <span class="actor-highlight">${escapeHtml(art.threat_actor)}</span></p>` : ''}
              ${mitigationsHtml ? `
                <div style="margin-top: 8px; font-weight: 600; color: var(--accent-emerald);">Actionable Defense:</div>
                <ul class="mitigation-checklist">${mitigationsHtml}</ul>
              ` : ''}
            </div>
          </div>
        </div>

        <div class="article-card-footer">
          <a href="${escapeHtml(art.url || '#')}" target="_blank" rel="noopener noreferrer" class="source-link-btn">
            <i class="fa-solid fa-arrow-up-right-from-square"></i> Full Source
          </a>
          <button class="card-copy-btn" onclick="copyCardDossier(${idx})" title="Copy Dossier to Clipboard">
            <i class="fa-regular fa-copy"></i> Copy Dossier
          </button>
        </div>
      </article>
    `;
  }).join('');
}

function toggleAccordion(btn) {
  const content = btn.nextElementSibling;
  const icon = btn.querySelector('.fa-chevron-down, .fa-chevron-up');
  const isOpen = content.classList.contains('open');
  
  content.classList.toggle('open');
  if (icon) {
    icon.classList.toggle('fa-chevron-down', isOpen);
    icon.classList.toggle('fa-chevron-up', !isOpen);
  }
}

function filterByCve(cve) {
  elements.searchInput.value = cve;
  state.searchQuery = cve.toLowerCase();
  elements.clearSearchBtn.classList.remove('hidden');
  applyFilters();
}

/**
 * Modal View
 */
function openDetailModal(articleIndex) {
  const art = state.filteredArticles[articleIndex];
  if (!art) return;

  elements.modalSevBadge.textContent = art.severity;
  elements.modalSevBadge.className = `modal-badge-sev tag-severity ${art.severity}`;
  elements.modalCategory.textContent = art.threat_category;

  const cves = (art.cve_ids || []).join(', ') || 'None assigned';
  const vendors = (art.affected_vendors || []).join(', ') || 'General Enterprise';
  const mitigations = (art.actionable_mitigations || []).map(m => `<li>${escapeHtml(m)}</li>`).join('');

  elements.modalBody.innerHTML = `
    <h2 style="font-family: var(--font-serif); font-size: 24px; color: #fff; margin-bottom: 16px;">${escapeHtml(art.title)}</h2>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px; font-size: 12px; background: var(--bg-surface); padding: 12px; border-radius: var(--radius-md);">
      <div><span style="color: var(--text-muted)">CVE Identifiers:</span> <strong style="color: var(--accent-red)">${escapeHtml(cves)}</strong></div>
      <div><span style="color: var(--text-muted)">Threat Actor:</span> <strong>${escapeHtml(art.threat_actor || 'Unknown')}</strong></div>
      <div><span style="color: var(--text-muted)">Affected Products:</span> <strong>${escapeHtml(vendors)}</strong></div>
      <div><span style="color: var(--text-muted)">Severity Rating:</span> <strong>${art.severity} (${art.severity_score || 'N/A'}/10)</strong></div>
    </div>

    <div style="margin-bottom: 16px;">
      <h4 style="color: #fff; margin-bottom: 6px; font-size: 14px;">Executive Brief</h4>
      <p style="color: var(--text-secondary); font-size: 13.5px;">${escapeHtml(art.executive_summary || '')}</p>
    </div>

    <div style="margin-bottom: 16px;">
      <h4 style="color: #fff; margin-bottom: 6px; font-size: 14px;">Technical Anatomy & Root Cause</h4>
      <p style="color: var(--text-secondary); font-size: 13.5px;">${escapeHtml(art.technical_breakdown || '')}</p>
    </div>

    <div>
      <h4 style="color: var(--accent-emerald); margin-bottom: 6px; font-size: 14px;">Defense & Actionable Mitigations</h4>
      <ul class="mitigation-checklist">${mitigations}</ul>
    </div>
  `;

  elements.modalSourceLink.href = art.url || '#';
  elements.modalCopyBtn.onclick = () => copyCardDossier(articleIndex);
  elements.modal.classList.remove('hidden');
}

function closeModal() {
  elements.modal.classList.add('hidden');
}

/**
 * Copy Actions
 */
function copyCardDossier(idx) {
  const art = state.filteredArticles[idx];
  if (!art) return;

  const text = `🛡️ [THREATBYTE] ${art.severity}: ${art.title}\n` +
               `Category: ${art.threat_category} | CVEs: ${(art.cve_ids || []).join(', ') || 'N/A'}\n\n` +
               `Executive Summary:\n${art.executive_summary}\n\n` +
               `Defense Recommendations:\n${(art.actionable_mitigations || []).map(m => '- ' + m).join('\n')}\n\n` +
               `Source: ${art.url}`;

  navigator.clipboard.writeText(text).then(() => {
    showToast('Threat dossier copied to clipboard!');
  });
}

function copyFullBriefingToClipboard() {
  if (!state.currentPayload || !state.allArticles.length) return;

  const date = state.currentPayload.date || 'Today';
  const lines = [
    `🛡️ THREATBYTE // DAILY CYBER INTELLIGENCE BRIEFING (${date})`,
    `Curated 24-hour threat telemetry across verified security sources.`,
    `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`,
    ``
  ];

  state.allArticles.slice(0, 5).forEach((art, i) => {
    lines.push(`${i + 1}. [${art.severity}] ${art.title}`);
    lines.push(`   ${art.executive_summary}`);
    lines.push(`   Link: ${art.url}`);
    lines.push(``);
  });

  lines.push(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
  lines.push(`🌐 Web Portal: ${window.location.href}`);
  lines.push(`📲 Daily Telegram Bot: https://t.me/threatbytebot`);

  navigator.clipboard.writeText(lines.join('\n')).then(() => {
    showToast('Full ThreatByte briefing copied for sharing!');
  });
}

function showToast(message) {
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.innerHTML = `<i class="fa-solid fa-circle-check" style="color: var(--accent-emerald)"></i> ${escapeHtml(message)}`;
  elements.toastContainer.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 250);
  }, 2800);
}

function formatTimeAgo(isoString) {
  if (!isoString) return 'Today';
  try {
    const diffHours = Math.round((new Date() - new Date(isoString)) / (1000 * 60 * 60));
    if (diffHours <= 1) return 'Just now';
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${Math.round(diffHours / 24)}d ago`;
  } catch (e) {
    return 'Today';
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
