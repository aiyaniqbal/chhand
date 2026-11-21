/**
 * CreatePage - Multilingual AI Poetry Studio.
 * Generates verified poetry in Hindi, Urdu, and Bengali with deterministic meter scanning.
 */

import { generatePoetry } from "./api.js";

const FORMS_BY_LANGUAGE = {
  hi: [
    { id: "doha", name: "दोहा (Doha)", desc: "13 · 11 · 13 · 11 matras" },
    { id: "chaupai", name: "चौपाई (Chaupai)", desc: "16 · 16 · 16 · 16 matras" },
    { id: "free_verse", name: "मुक्तक (Free Verse)", desc: "Unrestricted meter" },
  ],
  ur: [
    { id: "ghazal", name: "غزل (Ghazal)", desc: "Classical Bahr & Taqti (Hazaj / Ramal / Mutaqarib)" },
    { id: "nazm", name: "نظم (Nazm)", desc: "Thematic verse with recurring cadence" },
    { id: "free_verse", name: "آزاد نظم (Free Verse)", desc: "Modern unrestricted verse" },
  ],
  bn: [
    { id: "aksharbritta", name: "অক্ষরবৃত্ত (Aksharbritta / Payar)", desc: "14 aksharas (8 + 6)" },
    { id: "matrabritta", name: "মাত্রাবৃত্ত (Matrabritta)", desc: "Syllable-timed 6 + 6 rhythm" },
    { id: "swarobritta", name: "দলবৃত্ত / স্বরবৃত্ত (Swarabritta)", desc: "Folk stress meter (4 + 4 dals)" },
    { id: "free_verse", name: "মুক্ত ছন্দ (Free Verse)", desc: "Modern lyrical cadence" },
  ],
};

const SUGGESTED_THEMES = {
  hi: ["वर्षा और विरह", "प्रातःकाल का प्रकाश", "जीवन का पथ", "मौन और विचार", "मातृभूमि"],
  ur: ["شام اور تنہائی", "امیدِ سحر", "عشق و خاموشی", "یادوں کا کارواں", "جستجو"],
  bn: ["বৃষ্টি ও মেঘের গান", "শরতের নীল আকাশ", "জীবন ও নদীর বাঁক", "নিস্তব্ধতার সুর", "জ্যোৎস্না"],
};

export class CreatePage {
  constructor(options = {}) {
    this.container = document.getElementById("create-view");
    this.onSendToEditor = options.onSendToEditor || null;
    this.onSendToRecite = options.onSendToRecite || null;
    this.onOpenExport = options.onOpenExport || null;
    this.showToast = options.showToast || console.log;

    this.selectedLanguage = "hi";
    this.selectedForm = "doha";
    this.lastGeneratedPoem = null;
    this.isGenerating = false;

    this.render();
    this.bindEvents();
  }

  render() {
    if (!this.container) return;

    this.container.innerHTML = `
      <div class="create-studio-layout">
        
        <!-- Left: Configuration Form -->
        <section class="create-config-card" aria-label="AI Poetry Parameters">
          <div class="card-header-row">
            <div>
              <span class="card-kicker">AI CREATIVE STUDIO</span>
              <h2 class="section-title">Compose New Verse</h2>
            </div>
            <span class="badge-gemini">Gemini Powered</span>
          </div>
          <p class="section-desc">
            Generate authentic poetry in Hindi, Urdu, or Bengali. Every generated line is verified by Chhand's independent language prosody engine.
          </p>

          <!-- Language Selector -->
          <div class="form-group">
            <label class="form-label">Poetic Tradition & Language</label>
            <div class="lang-pill-selector" role="radiogroup" aria-label="Language">
              <button type="button" class="lang-pill active" data-lang="hi">
                <span class="lang-native">हिंदी</span>
                <span class="lang-sub">Hindi · Devanagari</span>
              </button>
              <button type="button" class="lang-pill" data-lang="ur">
                <span class="lang-native" style="font-family: 'Noto Nastaliq Urdu', serif;">اردو</span>
                <span class="lang-sub">Urdu · Nastaliq</span>
              </button>
              <button type="button" class="lang-pill" data-lang="bn">
                <span class="lang-native">বাংলা</span>
                <span class="lang-sub">Bengali · Chhanda</span>
              </button>
            </div>
          </div>

          <!-- Form / Meter Selector -->
          <div class="form-group">
            <label for="create-form-select" class="form-label">Poetic Form / Meter</label>
            <select id="create-form-select" class="form-select">
              <!-- Dynamically populated -->
            </select>
          </div>

          <!-- Theme & Suggestions -->
          <div class="form-group">
            <label for="create-theme-input" class="form-label">Theme / Seed Idea</label>
            <input type="text" id="create-theme-input" class="form-input" placeholder="e.g. Evening rain, contemplation, hope">
            <div id="theme-chips-wrap" class="theme-chips-row">
              <!-- Dynamically populated suggested themes -->
            </div>
          </div>

          <!-- Emotional Mood & Stanzas Grid -->
          <div class="form-row-grid">
            <div class="form-group">
              <label for="create-mood-select" class="form-label">Mood / Tone</label>
              <select id="create-mood-select" class="form-select">
                <option value="melancholic">Melancholic (विरह / حزن)</option>
                <option value="romantic" selected>Romantic (शृंगार / عشق)</option>
                <option value="devotional">Devotional (भक्ति / عقیدت)</option>
                <option value="philosophical">Philosophical (गंभीर / فلسفیانہ)</option>
                <option value="celebratory">Celebratory (उल्लास / جشن)</option>
              </select>
            </div>

            <div class="form-group">
              <label for="create-stanzas-select" class="form-label">Length</label>
              <select id="create-stanzas-select" class="form-select">
                <option value="1" selected>1 Stanza / Couplet</option>
                <option value="2">2 Stanzas</option>
                <option value="3">3 Stanzas</option>
              </select>
            </div>
          </div>

          <!-- Custom Instructions -->
          <div class="form-group">
            <label for="create-instructions-input" class="form-label">Special Instructions (Optional)</label>
            <input type="text" id="create-instructions-input" class="form-input" placeholder="e.g. Include imagery of clouds, use classical vocabulary">
          </div>

          <!-- Generate Action Button -->
          <button type="button" id="btn-generate-poem" class="btn-primary-action">
            <span id="generate-btn-text">Compose Poem</span>
            <span id="generate-spinner" class="spinner" style="display: none;"></span>
          </button>
        </section>

        <!-- Right: Generated Output Canvas -->
        <section class="create-output-card" aria-label="Generated Poem Output">
          <div class="output-header-row">
            <div>
              <span class="card-kicker">OUTPUT CANVAS</span>
              <h3 id="output-poem-title" class="output-title">Your Verse Appears Here</h3>
            </div>
            <div id="output-status-wrap" style="display: none;">
              <span id="output-validation-badge" class="badge-verification">Verified</span>
            </div>
          </div>

          <!-- Placeholder when empty -->
          <div id="create-placeholder" class="output-placeholder">
            <div class="placeholder-icon">✍</div>
            <p class="placeholder-text">
              Select your language and form on the left, then click <strong>Compose Poem</strong> to generate authentic verse.
            </p>
            <p class="placeholder-subtext">
              Chhand applies Gemini with rigorous classical scansion checks for Hindi matras, Urdu Bahrs, and Bengali dals.
            </p>
          </div>

          <!-- Generated Poem Display -->
          <div id="create-result-content" class="generated-poem-container" style="display: none;">
            <div id="generated-stanzas-wrap" class="generated-stanzas"></div>

            <div id="generated-validation-box" class="validation-summary-box"></div>

            <!-- Action Toolbar -->
            <div class="output-actions-row">
              <button type="button" id="btn-copy-generated" class="btn-secondary-action">
                📋 Copy Text
              </button>
              <button type="button" id="btn-open-in-editor" class="btn-secondary-action">
                ✏ Open in Editor
              </button>
              <button type="button" id="btn-recite-generated" class="btn-secondary-action">
                🎙 Recite Verse
              </button>
              <button type="button" id="btn-export-generated" class="btn-secondary-action">
                📄 Export Sheet
              </button>
            </div>
          </div>
        </section>

      </div>
    `;

    this.updateFormOptions();
    this.updateThemeChips();
  }

  bindEvents() {
    if (!this.container) return;

    // Language selector pills
    this.container.querySelectorAll(".lang-pill").forEach(pill => {
      pill.addEventListener("click", () => {
        this.container.querySelectorAll(".lang-pill").forEach(p => p.classList.remove("active"));
        pill.classList.add("active");
        this.selectedLanguage = pill.dataset.lang;
        this.updateFormOptions();
        this.updateThemeChips();
      });
    });

    // Form select change
    const formSelect = this.container.querySelector("#create-form-select");
    if (formSelect) {
      formSelect.addEventListener("change", (e) => {
        this.selectedForm = e.target.value;
      });
    }

    // Generate button
    const generateBtn = this.container.querySelector("#btn-generate-poem");
    if (generateBtn) {
      generateBtn.addEventListener("click", () => this.handleGenerate());
    }

    // Action buttons
    const btnCopy = this.container.querySelector("#btn-copy-generated");
    if (btnCopy) {
      btnCopy.addEventListener("click", () => this.copyToClipboard());
    }

    const btnEditor = this.container.querySelector("#btn-open-in-editor");
    if (btnEditor) {
      btnEditor.addEventListener("click", () => {
        if (this.onSendToEditor && this.lastGeneratedPoem) {
          this.onSendToEditor(this.lastGeneratedPoem);
        }
      });
    }

    const btnRecite = this.container.querySelector("#btn-recite-generated");
    if (btnRecite) {
      btnRecite.addEventListener("click", () => {
        if (this.onSendToRecite && this.lastGeneratedPoem) {
          this.onSendToRecite(this.lastGeneratedPoem);
        }
      });
    }

    const btnExport = this.container.querySelector("#btn-export-generated");
    if (btnExport) {
      btnExport.addEventListener("click", () => {
        if (this.onOpenExport && this.lastGeneratedPoem) {
          this.onOpenExport(this.lastGeneratedPoem);
        }
      });
    }
  }

  updateFormOptions() {
    const formSelect = this.container?.querySelector("#create-form-select");
    if (!formSelect) return;

    const forms = FORMS_BY_LANGUAGE[this.selectedLanguage] || FORMS_BY_LANGUAGE.hi;
    formSelect.innerHTML = forms
      .map(f => `<option value="${f.id}">${f.name} — ${f.desc}</option>`)
      .join("");
    this.selectedForm = forms[0].id;
  }

  updateThemeChips() {
    const chipsWrap = this.container?.querySelector("#theme-chips-wrap");
    const themeInput = this.container?.querySelector("#create-theme-input");
    if (!chipsWrap || !themeInput) return;

    const themes = SUGGESTED_THEMES[this.selectedLanguage] || SUGGESTED_THEMES.hi;
    chipsWrap.innerHTML = themes
      .map(t => `<button type="button" class="theme-chip" data-theme="${t}">${t}</button>`)
      .join("");

    chipsWrap.querySelectorAll(".theme-chip").forEach(chip => {
      chip.addEventListener("click", () => {
        themeInput.value = chip.dataset.theme;
        themeInput.focus();
      });
    });
  }

  async handleGenerate() {
    if (this.isGenerating) return;

    const themeInput = this.container.querySelector("#create-theme-input");
    const moodSelect = this.container.querySelector("#create-mood-select");
    const stanzasSelect = this.container.querySelector("#create-stanzas-select");
    const instructionsInput = this.container.querySelector("#create-instructions-input");
    const btnText = this.container.querySelector("#generate-btn-text");
    const spinner = this.container.querySelector("#generate-spinner");
    const generateBtn = this.container.querySelector("#btn-generate-poem");

    const payload = {
      language: this.selectedLanguage,
      poem_form: this.selectedForm,
      theme: themeInput?.value.trim() || "",
      mood: moodSelect?.value || "romantic",
      num_stanzas: parseInt(stanzasSelect?.value || "1", 10),
      instructions: instructionsInput?.value.trim() || "",
    };

    this.isGenerating = true;
    if (generateBtn) generateBtn.disabled = true;
    if (btnText) btnText.textContent = "Writing verse with Gemini...";
    if (spinner) spinner.style.display = "inline-block";

    try {
      const response = await generatePoetry(payload);
      this.lastGeneratedPoem = response;
      this.renderPoemResult(response);
      this.showToast("Poem generated and verified successfully!");
    } catch (err) {
      this.showToast(`Generation error: ${err.message}`);
    } finally {
      this.isGenerating = false;
      if (generateBtn) generateBtn.disabled = false;
      if (btnText) btnText.textContent = "Compose Poem";
      if (spinner) spinner.style.display = "none";
    }
  }

  renderPoemResult(response) {
    const placeholder = this.container.querySelector("#create-placeholder");
    const resultContent = this.container.querySelector("#create-result-content");
    const stanzasWrap = this.container.querySelector("#generated-stanzas-wrap");
    const validationBox = this.container.querySelector("#generated-validation-box");
    const statusWrap = this.container.querySelector("#output-status-wrap");
    const badge = this.container.querySelector("#output-validation-badge");
    const title = this.container.querySelector("#output-poem-title");

    if (placeholder) placeholder.style.display = "none";
    if (resultContent) resultContent.style.display = "block";
    if (statusWrap) statusWrap.style.display = "block";

    const isUrdu = response.language === "ur";
    const isBengali = response.language === "bn";

    if (title) {
      const theme = this.container.querySelector("#create-theme-input")?.value.trim();
      title.textContent = theme || (isUrdu ? "نئی تخلیق" : isBengali ? "নতুন কবিতা" : "रचना");
    }

    // Validation badge styling
    const val = response.validation || {};
    const isValid = val.overall_status === "valid" || val.overall_status === "verified";
    if (badge) {
      badge.textContent = isValid ? "✓ Meter Verified" : "Partial Scansion";
      badge.className = isValid ? "badge-verification verified" : "badge-verification partial";
    }

    // Render stanzas
    if (stanzasWrap) {
      stanzasWrap.innerHTML = (response.stanzas || []).map((stanza, sIdx) => {
        const linesHtml = stanza.map((line, lIdx) => {
          const statusClass = line.validation_status === "matched" ? "valid" : "warning";
          const countInfo = line.matra_count ? `${line.matra_count} units` : "";
          const noteInfo = line.validation_note ? `· ${line.validation_note}` : "";

          return `
            <div class="generated-line-row ${statusClass} ${isUrdu ? 'rtl-text' : ''} ${isBengali ? 'bengali-text' : ''}" dir="${isUrdu ? 'rtl' : 'ltr'}">
              <span class="line-index">${sIdx * stanza.length + lIdx + 1}</span>
              <div class="line-text-wrap">
                <p class="line-text ${isUrdu ? 'urdu-text' : ''}">${line.text}</p>
                <div class="line-meta">
                  <span class="meta-tag ${statusClass}">${line.validation_status}</span>
                  ${countInfo ? `<span class="meta-count">${countInfo}</span>` : ""}
                  ${noteInfo ? `<span class="meta-note">${noteInfo}</span>` : ""}
                </div>
              </div>
            </div>
          `;
        }).join("");

        return `<div class="stanza-card">${linesHtml}</div>`;
      }).join("");
    }

    // Validation summary box
    if (validationBox) {
      const notesHtml = (val.notes || []).map(n => `<li>${n}</li>`).join("");
      const matches = val.meter_matches ?? val.validated_lines ?? 0;
      const total = val.total_units ?? val.total_lines ?? 0;

      validationBox.innerHTML = `
        <div class="val-summary-header">
          <strong>Engine Verification:</strong> ${matches} of ${total} lines verified strictly against classical prosody.
        </div>
        ${notesHtml ? `<ul class="val-summary-notes">${notesHtml}</ul>` : ""}
      `;
    }
  }

  copyToClipboard() {
    if (!this.lastGeneratedPoem) return;
    const textLines = (this.lastGeneratedPoem.stanzas || [])
      .map(stanza => stanza.map(l => l.text).join("\n"))
      .join("\n\n");

    navigator.clipboard.writeText(textLines).then(() => {
      this.showToast("Poem copied to clipboard!");
    }).catch(() => {
      this.showToast("Failed to copy poem.");
    });
  }
}
