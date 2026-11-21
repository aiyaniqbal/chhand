/**
 * RecitePage - Text-to-Speech Poetry Recitation Studio for Chhand.
 * Sequential line-by-line synthesis, audio playback, and active visual line tracking.
 */

import { fetchStyles, fetchVoices, synthesizeSpeech } from "./api.js";

export class RecitePage {
  constructor(options = {}) {
    this.container = document.getElementById("recite-view");
    this.showToast = options.showToast || console.log;
    this.getEditorPoem = options.getEditorPoem || null;

    this.selectedLanguage = "hi";
    this.selectedVoice = "Kore";
    this.selectedStyle = "natural poetry recitation";

    this.lines = [
      "उदित उदय गिरि मंच पर, रघुबर बाल पतंग।",
      "बिकसे संत सरोज सब, हरषे लोचन भृंग॥",
    ];

    this.isPlaying = false;
    this.isPaused = false;
    this.currentPlayingIndex = -1;
    this.audioCache = new Map(); // lineText -> blobUrl
    this.currentAudioElement = null;

    this.render();
    this.loadVoicesAndStyles();
    this.bindEvents();
  }

  render() {
    if (!this.container) return;

    this.container.innerHTML = `
      <div class="recite-studio-layout">
        
        <!-- Top Toolbar / Master Controller -->
        <section class="recite-controller-card" aria-label="Recitation Controls">
          <div class="card-header-row">
            <div>
              <span class="card-kicker">GEMINI TTS AUDIO STUDIO</span>
              <h2 class="section-title">Poetry Recitation</h2>
            </div>
            <span class="badge-gemini">24kHz Audio</span>
          </div>
          <p class="section-desc">
            Listen to verses recited with cadence, pauses, and expression. Select voice and cadence style below.
          </p>

          <div class="recite-controls-grid">
            
            <!-- Language Selector -->
            <div class="form-group">
              <label for="recite-lang-select" class="form-label">Language</label>
              <select id="recite-lang-select" class="form-select">
                <option value="hi" selected>Hindi (हिंदी)</option>
                <option value="bn">Bengali (বাংলা)</option>
                <option value="ur">Urdu (اردو - Experimental)</option>
              </select>
            </div>

            <!-- Voice Selector -->
            <div class="form-group">
              <label for="recite-voice-select" class="form-label">Voice</label>
              <select id="recite-voice-select" class="form-select">
                <option value="Kore" selected>Kore (Balanced & Warm)</option>
                <option value="Puck">Puck (Resonant & Expressive)</option>
                <option value="Fenrir">Fenrir (Deep & Classical)</option>
                <option value="Aoede">Aoede (Melodic & Gentle)</option>
                <option value="Charon">Charon (Solemn & Rich)</option>
              </select>
            </div>

            <!-- Style Selector -->
            <div class="form-group">
              <label for="recite-style-select" class="form-label">Recitation Cadence</label>
              <select id="recite-style-select" class="form-select">
                <option value="natural poetry recitation" selected>Natural Poetry Recitation</option>
                <option value="slow meditative reading">Slow Meditative Cadence</option>
                <option value="dramatic emotional cadence">Dramatic Emotional Tone</option>
                <option value="conversational lyric reading">Conversational Lyric</option>
              </select>
            </div>

          </div>

          <!-- Playback Actions -->
          <div class="playback-bar-row">
            <button type="button" id="btn-play-all" class="btn-primary-action playback-btn">
              <span id="play-all-icon">▶</span>
              <span id="play-all-text">Recite All Lines</span>
            </button>
            <button type="button" id="btn-stop-recite" class="btn-secondary-action" disabled>
              ⏹ Stop
            </button>
            <span id="recite-status-label" class="recite-status-label">Ready to recite</span>
          </div>
        </section>

        <!-- Main Studio Grid: Lines on Left, Quick Input on Right -->
        <div class="recite-content-grid">
          
          <!-- Left: Interactive Line Cards with Playback Progress -->
          <section class="recite-lines-card" aria-label="Verse Lines Progression">
            <div class="card-header-row">
              <span class="card-kicker">RECITER TIMELINE</span>
              <span id="recite-lines-count-badge" class="badge-count">${this.lines.length} Lines</span>
            </div>
            
            <div id="recite-lines-list" class="recite-lines-list">
              <!-- Dynamically populated line cards -->
            </div>
          </section>

          <!-- Right: Text Input / Quick Import -->
          <section class="recite-input-card" aria-label="Poem Text Input">
            <div class="card-header-row">
              <span class="card-kicker">POEM TEXT</span>
              <div class="quick-import-actions">
                <button type="button" id="btn-load-from-editor" class="btn-link-action">From Poems Editor</button>
              </div>
            </div>

            <textarea id="recite-poem-textarea" class="recite-textarea" placeholder="Paste or type poem lines here (one line per verse)..." rows="6">${this.lines.join("\n")}</textarea>

            <button type="button" id="btn-update-recite-lines" class="btn-secondary-action full-width" style="margin-top: 0.75rem;">
              Update Reciter Lines
            </button>
          </section>

        </div>

      </div>
    `;

    this.renderLinesList();
  }

  async loadVoicesAndStyles() {
    try {
      const voices = await fetchVoices();
      const voiceSelect = this.container?.querySelector("#recite-voice-select");
      if (voiceSelect && voices && voices.length > 0) {
        voiceSelect.innerHTML = voices
          .map(v => `<option value="${v}">${v}</option>`)
          .join("");
        this.selectedVoice = voices[0];
      }

      const styles = await fetchStyles();
      const styleSelect = this.container?.querySelector("#recite-style-select");
      if (styleSelect && styles && styles.length > 0) {
        styleSelect.innerHTML = styles
          .map(s => `<option value="${s}">${s}</option>`)
          .join("");
        this.selectedStyle = styles[0];
      }
    } catch (_) {
      // Fallbacks already in HTML
    }
  }

  bindEvents() {
    if (!this.container) return;

    // Language Select
    const langSelect = this.container.querySelector("#recite-lang-select");
    if (langSelect) {
      langSelect.addEventListener("change", (e) => {
        this.selectedLanguage = e.target.value;
        this.audioCache.clear();
        this.renderLinesList();
      });
    }

    // Voice & Style Selects
    const voiceSelect = this.container.querySelector("#recite-voice-select");
    if (voiceSelect) {
      voiceSelect.addEventListener("change", (e) => {
        this.selectedVoice = e.target.value;
        this.audioCache.clear();
      });
    }

    const styleSelect = this.container.querySelector("#recite-style-select");
    if (styleSelect) {
      styleSelect.addEventListener("change", (e) => {
        this.selectedStyle = e.target.value;
        this.audioCache.clear();
      });
    }

    // Play All Button
    const btnPlayAll = this.container.querySelector("#btn-play-all");
    if (btnPlayAll) {
      btnPlayAll.addEventListener("click", () => {
        if (this.isPlaying) {
          this.stopPlayback();
        } else {
          this.playAllLines();
        }
      });
    }

    // Stop Button
    const btnStop = this.container.querySelector("#btn-stop-recite");
    if (btnStop) {
      btnStop.addEventListener("click", () => this.stopPlayback());
    }

    // Update Lines Button
    const btnUpdate = this.container.querySelector("#btn-update-recite-lines");
    const textarea = this.container.querySelector("#recite-poem-textarea");
    if (btnUpdate && textarea) {
      btnUpdate.addEventListener("click", () => {
        const text = textarea.value.trim();
        if (!text) {
          this.showToast("Please enter at least one poem line.");
          return;
        }
        this.stopPlayback();
        this.audioCache.clear();
        this.lines = text.split("\n").map(l => l.trim()).filter(Boolean);
        this.renderLinesList();
        this.showToast(`Updated with ${this.lines.length} lines.`);
      });
    }

    // Load from Editor Button
    const btnLoadEditor = this.container.querySelector("#btn-load-from-editor");
    if (btnLoadEditor) {
      btnLoadEditor.addEventListener("click", () => {
        if (this.getEditorPoem) {
          const editorLines = this.getEditorPoem();
          if (editorLines && editorLines.length > 0) {
            this.setPoemLines(editorLines, "hi");
            this.showToast("Loaded lines from Poems editor.");
          } else {
            this.showToast("No lines found in Poems editor.");
          }
        }
      });
    }
  }

  setPoemLines(lines, language = "hi") {
    this.stopPlayback();
    this.audioCache.clear();
    this.lines = lines.filter(Boolean);
    this.selectedLanguage = language;

    const langSelect = this.container?.querySelector("#recite-lang-select");
    if (langSelect) langSelect.value = language;

    const textarea = this.container?.querySelector("#recite-poem-textarea");
    if (textarea) textarea.value = this.lines.join("\n");

    this.renderLinesList();
  }

  renderLinesList() {
    const list = this.container?.querySelector("#recite-lines-list");
    const countBadge = this.container?.querySelector("#recite-lines-count-badge");
    if (countBadge) countBadge.textContent = `${this.lines.length} Lines`;
    if (!list) return;

    const isUrdu = this.selectedLanguage === "ur";
    const isBengali = this.selectedLanguage === "bn";

    list.innerHTML = this.lines.map((line, idx) => {
      const isCurrent = this.currentPlayingIndex === idx;
      return `
        <div class="recite-line-card ${isCurrent ? 'playing' : ''} ${isUrdu ? 'rtl-text' : ''} ${isBengali ? 'bengali-text' : ''}" data-idx="${idx}" dir="${isUrdu ? 'rtl' : 'ltr'}">
          <div class="recite-line-num">${idx + 1}</div>
          <div class="recite-line-body">
            <p class="recite-line-text ${isUrdu ? 'urdu-text' : ''}">${line}</p>
          </div>
          <div class="recite-line-actions">
            <button type="button" class="btn-solo-play" data-idx="${idx}" title="Recite this line">
              ${isCurrent ? '🔊' : '▶'}
            </button>
          </div>
        </div>
      `;
    }).join("");

    // Bind individual solo-play buttons
    list.querySelectorAll(".btn-solo-play").forEach(btn => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const idx = parseInt(btn.dataset.idx, 10);
        this.playSingleLine(idx);
      });
    });
  }

  async playSingleLine(idx) {
    if (idx < 0 || idx >= this.lines.length) return;
    this.stopPlayback();

    const line = this.lines[idx];
    this.currentPlayingIndex = idx;
    this.renderLinesList();
    this.setStatus(`Synthesizing line ${idx + 1}...`);

    try {
      const audioUrl = await this.getAudioForLine(line);
      this.setStatus(`Reciting line ${idx + 1}...`);
      await this.playAudioUrl(audioUrl);
    } catch (err) {
      this.showToast(`TTS error: ${err.message}`);
    } finally {
      this.currentPlayingIndex = -1;
      this.renderLinesList();
      this.setStatus("Ready to recite");
    }
  }

  async playAllLines() {
    if (this.lines.length === 0) {
      this.showToast("No lines to recite.");
      return;
    }

    this.isPlaying = true;
    const btnPlayAll = this.container?.querySelector("#btn-play-all");
    const playIcon = this.container?.querySelector("#play-all-icon");
    const playText = this.container?.querySelector("#play-all-text");
    const btnStop = this.container?.querySelector("#btn-stop-recite");

    if (playIcon) playIcon.textContent = "⏹";
    if (playText) playText.textContent = "Stop Recitation";
    if (btnStop) btnStop.disabled = false;

    for (let i = 0; i < this.lines.length; i++) {
      if (!this.isPlaying) break;

      this.currentPlayingIndex = i;
      this.renderLinesList();
      this.setStatus(`Reciting line ${i + 1} of ${this.lines.length}...`);

      try {
        const audioUrl = await this.getAudioForLine(this.lines[i]);
        if (!this.isPlaying) break;
        await this.playAudioUrl(audioUrl);
      } catch (err) {
        this.showToast(`Line ${i + 1} TTS error: ${err.message}`);
      }

      // Natural poetic caesura pause between lines
      if (this.isPlaying && i < this.lines.length - 1) {
        await new Promise(r => setTimeout(r, 600));
      }
    }

    this.stopPlayback();
  }

  stopPlayback() {
    this.isPlaying = false;
    this.currentPlayingIndex = -1;

    if (this.currentAudioElement) {
      this.currentAudioElement.pause();
      this.currentAudioElement.currentTime = 0;
      this.currentAudioElement = null;
    }

    const playIcon = this.container?.querySelector("#play-all-icon");
    const playText = this.container?.querySelector("#play-all-text");
    const btnStop = this.container?.querySelector("#btn-stop-recite");

    if (playIcon) playIcon.textContent = "▶";
    if (playText) playText.textContent = "Recite All Lines";
    if (btnStop) btnStop.disabled = true;

    this.setStatus("Playback stopped");
    this.renderLinesList();
  }

  async getAudioForLine(line) {
    const cacheKey = `${this.selectedLanguage}:${this.selectedVoice}:${this.selectedStyle}:${line}`;
    if (this.audioCache.has(cacheKey)) {
      return this.audioCache.get(cacheKey);
    }

    const blob = await synthesizeSpeech({
      text: line,
      language: this.selectedLanguage,
      voice: this.selectedVoice,
      style: this.selectedStyle,
    });

    const url = URL.createObjectURL(blob);
    this.audioCache.set(cacheKey, url);
    return url;
  }

  playAudioUrl(url) {
    return new Promise((resolve, reject) => {
      const audio = new Audio(url);
      this.currentAudioElement = audio;

      audio.onended = () => {
        this.currentAudioElement = null;
        resolve();
      };

      audio.onerror = (e) => {
        this.currentAudioElement = null;
        reject(new Error("Audio playback failed"));
      };

      audio.play().catch(reject);
    });
  }

  setStatus(text) {
    const label = this.container?.querySelector("#recite-status-label");
    if (label) label.textContent = text;
  }
}
