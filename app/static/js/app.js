/**
 * Neural Translation Studio — Client Application Logic
 */

document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements - Studio
  const srcInput = document.getElementById("source-input");
  const tgtOutput = document.getElementById("target-output");
  const srcLangSelect = document.getElementById("src-lang-select");
  const tgtLangSelect = document.getElementById("tgt-lang-select");
  const swapBtn = document.getElementById("swap-lang-btn");
  const clearBtn = document.getElementById("clear-btn");
  const copyBtn = document.getElementById("copy-btn");
  const translateBtn = document.getElementById("translate-btn");
  const detectLangBtn = document.getElementById("detect-lang-btn");
  const detectionBadge = document.getElementById("detection-badge");
  const srcCharCount = document.getElementById("src-char-count");
  const srcWordCount = document.getElementById("src-word-count");
  const latencyMetric = document.getElementById("latency-metric");
  const tokensMetric = document.getElementById("tokens-metric");
  const termsAuditBadge = document.getElementById("terms-audit-badge");
  const protectTermsToggle = document.getElementById("protect-terms-toggle");
  const numBeamsSlider = document.getElementById("num-beams-slider");
  const beamValDisplay = document.getElementById("beam-val");
  const maxTokensSlider = document.getElementById("max-tokens-slider");
  const maxTokensValDisplay = document.getElementById("max-tokens-val");
  const diagnosticsPanel = document.getElementById("diagnostics-panel");
  const diagnosticsContent = document.getElementById("diagnostics-content");
  const dismissDiagBtn = document.getElementById("dismiss-diag-btn");
  const engineStatusPill = document.getElementById("engine-status-pill");
  const engineStatusText = document.getElementById("engine-status-text");

  // DOM Elements - Tabs & Others
  const tabButtons = document.querySelectorAll(".tab-btn");
  const tabPanels = document.querySelectorAll(".tab-panel");
  const scenariosContainer = document.getElementById("scenarios-container");
  const glossaryTagsContainer = document.getElementById("glossary-tags");
  const newTermInput = document.getElementById("new-term-input");
  const addTermBtn = document.getElementById("add-term-btn");
  const saveGlossaryBtn = document.getElementById("save-glossary-btn");
  const quickPresetChips = document.getElementById("quick-preset-chips");

  let currentGlossary = [];
  let sampleScenarios = [];

  // ==========================================================================
  // Tab Switching
  // ==========================================================================
  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-tab");
      tabButtons.forEach(b => b.classList.remove("active"));
      tabPanels.forEach(p => p.classList.remove("active"));
      btn.classList.add("active");
      const targetPanel = document.getElementById(targetId);
      if (targetPanel) targetPanel.classList.add("active");
    });
  });

  // ==========================================================================
  // Slider Value Displays
  // ==========================================================================
  numBeamsSlider.addEventListener("input", (e) => {
    beamValDisplay.textContent = `${e.target.value} beams`;
  });

  maxTokensSlider.addEventListener("input", (e) => {
    maxTokensValDisplay.textContent = `${e.target.value} tokens`;
  });

  // ==========================================================================
  // Input Counters & Text Management
  // ==========================================================================
  const updateCounters = () => {
    const text = srcInput.value;
    const chars = text.length;
    const words = text.trim() ? text.trim().split(/\s+/).length : 0;
    srcCharCount.textContent = `${chars} character${chars === 1 ? "" : "s"}`;
    srcWordCount.textContent = `${words} word${words === 1 ? "" : "s"}`;
  };

  srcInput.addEventListener("input", updateCounters);

  clearBtn.addEventListener("click", () => {
    srcInput.value = "";
    tgtOutput.innerHTML = "Translated output will appear here with technical terms, error codes, and URLs verified...";
    tgtOutput.classList.add("placeholder-state");
    latencyMetric.textContent = "Latency: —";
    tokensMetric.textContent = "Tokens: —";
    termsAuditBadge.className = "badge badge-neutral";
    termsAuditBadge.textContent = "No entities detected";
    detectionBadge.className = "badge badge-subtle";
    detectionBadge.textContent = srcLangSelect.value === "auto" ? "Auto Mode Ready" : `${srcLangSelect.value}`;
    diagnosticsPanel.classList.add("hidden");
    updateCounters();
  });

  // ==========================================================================
  // Swap Languages
  // ==========================================================================
  swapBtn.addEventListener("click", () => {
    const currentSrc = srcLangSelect.value;
    const currentTgt = tgtLangSelect.value;

    if (currentSrc === "auto") {
      srcLangSelect.value = currentTgt;
      tgtLangSelect.value = "English";
    } else {
      srcLangSelect.value = currentTgt;
      tgtLangSelect.value = currentSrc;
    }

    // If there is translated text, move target to source
    const currentTranslation = tgtOutput.textContent.trim();
    if (currentTranslation && !tgtOutput.classList.contains("placeholder-state")) {
      srcInput.value = currentTranslation;
      tgtOutput.innerHTML = "Translated output will appear here...";
      tgtOutput.classList.add("placeholder-state");
      updateCounters();
    }
  });

  // ==========================================================================
  // Copy to Clipboard
  // ==========================================================================
  copyBtn.addEventListener("click", async () => {
    if (tgtOutput.classList.contains("placeholder-state")) return;
    const text = tgtOutput.textContent.trim();
    if (!text) return;

    try {
      await navigator.clipboard.writeText(text);
      copyBtn.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
      `;
      setTimeout(() => {
        copyBtn.innerHTML = `
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
          </svg>
        `;
      }, 1800);
    } catch (err) {
      console.error("Clipboard copy failed:", err);
    }
  });

  // ==========================================================================
  // Language Detection Action
  // ==========================================================================
  detectLangBtn.addEventListener("click", async () => {
    const text = srcInput.value.trim();
    if (!text) {
      alert("Please enter some text in the source box to detect language.");
      return;
    }

    detectLangBtn.disabled = true;
    detectLangBtn.innerHTML = `<span>Detecting...</span>`;

    try {
      const resp = await fetch("/api/v1/detect-language", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: text,
          source_lang_override: srcLangSelect.value === "auto" ? null : srcLangSelect.value,
        }),
      });

      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();

      detectionBadge.className = "badge badge-success";
      detectionBadge.textContent = `${data.language_name} (${data.flores_code}) • ${(data.confidence * 100).toFixed(0)}%`;

      if (data.is_code_switched_suspect) {
        detectionBadge.className = "badge badge-warning";
        detectionBadge.textContent += " [Multilingual]";
      }
    } catch (err) {
      console.error("Language detection failed:", err);
      detectionBadge.className = "badge badge-danger";
      detectionBadge.textContent = "Detection Failed";
    } finally {
      detectLangBtn.disabled = false;
      detectLangBtn.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/>
          <line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        Detect Language
      `;
    }
  });

  // ==========================================================================
  // Translation Core Trigger
  // ==========================================================================
  const triggerTranslation = async () => {
    const message = srcInput.value.trim();
    if (!message) {
      alert("Please enter a customer message or ticket to translate.");
      return;
    }

    translateBtn.disabled = true;
    translateBtn.innerHTML = `
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin">
        <circle cx="12" cy="12" r="10" stroke-opacity="0.25"/>
        <path d="M12 2a10 10 0 0 1 10 10"/>
      </svg>
      <span>Translating...</span>
    `;

    tgtOutput.innerHTML = `<span style="color:var(--text-muted); font-style:italic;">Processing neural translation with entity preservation...</span>`;
    tgtOutput.classList.remove("placeholder-state");

    const payload = {
      message: message,
      target_lang: tgtLangSelect.value,
      source_lang: srcLangSelect.value === "auto" ? null : srcLangSelect.value,
      protect_terms: protectTermsToggle.checked,
      num_beams: parseInt(numBeamsSlider.value, 10),
      max_new_tokens: parseInt(maxTokensSlider.value, 10),
    };

    try {
      const resp = await fetch("/api/v1/translate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await resp.json();

      if (data.status === "error") {
        tgtOutput.innerHTML = `<span style="color:var(--danger); font-weight:600;">[Error] ${data.error}</span>`;
        termsAuditBadge.className = "badge badge-danger";
        termsAuditBadge.textContent = "Translation Failed";
        return;
      }

      // Success
      tgtOutput.textContent = data.translated_text;

      // Update detection badge
      detectionBadge.className = "badge badge-success";
      detectionBadge.textContent = `${data.source_language} (${data.source_flores_code})`;

      // Update Metrics
      latencyMetric.textContent = `Latency: ${data.latency_sec}s`;
      tokensMetric.textContent = `Tokens: ${data.input_token_count} in / ${data.output_token_count} out`;

      // Update Entity Preservation Badge
      if (data.protected_terms && data.protected_terms.length > 0) {
        if (data.all_terms_preserved) {
          termsAuditBadge.className = "badge badge-success";
          termsAuditBadge.textContent = `✓ ${data.protected_terms.length} Entities Preserved`;
        } else {
          termsAuditBadge.className = "badge badge-warning";
          termsAuditBadge.textContent = `⚠ Missing: ${data.missing_terms.join(", ")}`;
        }
      } else {
        termsAuditBadge.className = "badge badge-neutral";
        termsAuditBadge.textContent = "No entities in text";
      }

      // Render Diagnostics
      renderDiagnostics(data);

    } catch (err) {
      console.error("Translation request error:", err);
      tgtOutput.innerHTML = `<span style="color:var(--danger); font-weight:600;">[Network Error] Unable to connect to translation server.</span>`;
    } finally {
      translateBtn.disabled = false;
      translateBtn.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="5 3 19 12 5 21 5 3"/>
        </svg>
        <span>Translate Message</span>
      `;
    }
  };

  translateBtn.addEventListener("click", triggerTranslation);

  // Render Diagnostics Box
  const renderDiagnostics = (data) => {
    diagnosticsPanel.classList.remove("hidden");
    let html = `
      <div class="diag-item"><strong>Language Direction:</strong> ${data.source_language} (<code>${data.source_flores_code}</code>) &rarr; ${data.target_language} (<code>${data.target_flores_code}</code>)</div>
      <div class="diag-item"><strong>Detection Method:</strong> ${data.detection_method || "Direct"} (Confidence: ${data.detection_confidence ? (data.detection_confidence * 100).toFixed(1) + "%" : "100%"})</div>
    `;

    if (data.protected_terms && data.protected_terms.length > 0) {
      html += `<div class="diag-item"><strong>Protected Technical Entities:</strong> <code>${data.protected_terms.join(", ")}</code></div>`;
    }

    if (data.warnings && data.warnings.length > 0) {
      html += `<div class="diag-item" style="color:var(--warning);"><strong>Pipeline Notices:</strong><ul>${data.warnings.map(w => `<li>${w}</li>`).join("")}</ul></div>`;
    }

    diagnosticsContent.innerHTML = html;
  };

  dismissDiagBtn.addEventListener("click", () => {
    diagnosticsPanel.classList.add("hidden");
  });

  // ==========================================================================
  // Sample Presets & Quickbar
  // ==========================================================================
  quickPresetChips.addEventListener("click", (e) => {
    const chip = e.target.closest(".chip");
    if (!chip) return;
    const sampleId = chip.getAttribute("data-sample");
    loadSampleIntoStudio(sampleId);
  });

  const loadSampleIntoStudio = (sampleId) => {
    const found = sampleScenarios.find(s => s.id === sampleId);
    if (!found) return;

    srcInput.value = found.message;
    srcLangSelect.value = found.source_lang;
    tgtLangSelect.value = found.target_lang;
    updateCounters();

    // Switch to Studio tab
    document.querySelector('.tab-btn[data-tab="studio-tab"]').click();

    // Trigger translation automatically
    triggerTranslation();
  };

  // ==========================================================================
  // Load Curated Scenarios
  // ==========================================================================
  const loadScenarios = async () => {
    try {
      const resp = await fetch("/api/v1/samples");
      sampleScenarios = await resp.json();

      scenariosContainer.innerHTML = sampleScenarios.map(s => `
        <div class="scenario-card">
          <div class="scenario-top">
            <span class="scenario-badge">${s.category}</span>
            <span class="scenario-dir">${s.source_lang} &rarr; ${s.target_lang}</span>
          </div>
          <p class="scenario-desc">${s.description}</p>
          <div class="scenario-msg">${escapeHtml(s.message)}</div>
          <button class="btn btn-secondary btn-sm" onclick="window.tryScenario('${s.id}')">
            ⚡ Test in Studio
          </button>
        </div>
      `).join("");
    } catch (err) {
      console.error("Failed to load sample scenarios:", err);
    }
  };

  window.tryScenario = (sampleId) => {
    loadSampleIntoStudio(sampleId);
  };

  // ==========================================================================
  // Glossary Manager
  // ==========================================================================
  const loadGlossary = async () => {
    try {
      const resp = await fetch("/api/v1/glossary");
      const data = await resp.json();
      currentGlossary = data.terms || [];
      renderGlossaryTags();
    } catch (err) {
      console.error("Failed to load glossary:", err);
    }
  };

  const renderGlossaryTags = () => {
    glossaryTagsContainer.innerHTML = currentGlossary.map((term, index) => `
      <span class="term-tag">
        ${escapeHtml(term)}
        <button type="button" onclick="window.removeGlossaryTerm(${index})" title="Remove term">&times;</button>
      </span>
    `).join("");
  };

  window.removeGlossaryTerm = (index) => {
    currentGlossary.splice(index, 1);
    renderGlossaryTags();
  };

  addTermBtn.addEventListener("click", () => {
    const val = newTermInput.value.trim();
    if (!val) return;
    if (!currentGlossary.includes(val)) {
      currentGlossary.push(val);
      renderGlossaryTags();
    }
    newTermInput.value = "";
  });

  newTermInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      addTermBtn.click();
    }
  });

  saveGlossaryBtn.addEventListener("click", async () => {
    saveGlossaryBtn.disabled = true;
    saveGlossaryBtn.textContent = "Saving...";

    try {
      const resp = await fetch("/api/v1/glossary", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ terms: currentGlossary }),
      });
      if (resp.ok) {
        saveGlossaryBtn.textContent = "Saved ✓";
        setTimeout(() => { saveGlossaryBtn.textContent = "Save Glossary Changes"; }, 2000);
      }
    } catch (err) {
      console.error("Save glossary error:", err);
      alert("Failed to save glossary changes.");
    } finally {
      saveGlossaryBtn.disabled = false;
    }
  });

  // ==========================================================================
  // Engine Health Check
  // ==========================================================================
  const checkHealth = async () => {
    try {
      const resp = await fetch("/api/v1/health");
      const health = await resp.json();

      if (health.status === "online") {
        engineStatusPill.className = "status-indicator online";
        engineStatusText.textContent = `Online • ${health.device.toUpperCase()}`;
      } else {
        engineStatusPill.className = "status-indicator";
        engineStatusText.textContent = `Warning: ${health.status}`;
      }
    } catch (err) {
      engineStatusPill.className = "status-indicator";
      engineStatusText.textContent = "Offline";
    }
  };

  // Helper
  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  // Initial Boot
  checkHealth();
  loadScenarios();
  loadGlossary();
  updateCounters();
});
