/**
 * ExportPanel - Professional Lyric Sheet Exporter for Chhand.
 * Manages modal configuration, plain text download, and print-ready HTML generation.
 */

import { exportPoem } from "./api.js";

export class ExportPanel {
  constructor(options = {}) {
    this.modal = document.getElementById("export-modal");
    this.showToast = options.showToast || console.log;
    this.currentLines = [];
    this.currentLanguage = "hi";
    this.currentTitle = "मेरी रचना";
    this.currentMeter = "दोहा";

    this.renderModal();
    this.bindEvents();
  }

  renderModal() {
    if (!this.modal) return;

    this.modal.innerHTML = `
      <div class="modal-dialog export-dialog" role="dialog" aria-labelledby="export-modal-title" aria-modal="true">
        <div class="modal-header">
          <div class="modal-title-wrap">
            <span class="card-kicker">LYRIC SHEET EXPORT</span>
            <h3 id="export-modal-title" class="modal-title">Export Professional Sheet</h3>
          </div>
          <button type="button" id="btn-close-export-modal" class="btn-close-modal" aria-label="Close dialog">✕</button>
        </div>

        <div class="modal-body">
          <p class="modal-desc">
            Generate clean, publication-ready lyric sheets with typography and formatting tailored for Hindi, Urdu, or Bengali.
          </p>

          <form id="export-form" onsubmit="return false;">
            <div class="form-row-grid">
              <div class="form-group">
                <label for="export-title-input" class="form-label">Poem Title</label>
                <input type="text" id="export-title-input" class="form-input" value="${this.currentTitle}">
              </div>

              <div class="form-group">
                <label for="export-author-input" class="form-label">Poet / Author Name</label>
                <input type="text" id="export-author-input" class="form-input" placeholder="e.g. कबीर, ग़ालिब, or your name">
              </div>
            </div>

            <div class="form-row-grid">
              <div class="form-group">
                <label for="export-lang-select" class="form-label">Language & Script</label>
                <select id="export-lang-select" class="form-select">
                  <option value="hi" selected>Hindi (Devanagari)</option>
                  <option value="ur">Urdu (Nastaliq · RTL)</option>
                  <option value="bn">Bengali (Bangla)</option>
                </select>
              </div>

              <div class="form-group">
                <label for="export-meter-input" class="form-label">Meter / Chhand (Optional)</label>
                <input type="text" id="export-meter-input" class="form-input" value="${this.currentMeter}">
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Export Format</label>
              <div class="format-options-row">
                <label class="format-radio-label">
                  <input type="radio" name="export-format" value="html" checked>
                  <div class="format-card">
                    <span class="format-icon">🖨</span>
                    <span class="format-name">Print-Ready HTML</span>
                    <span class="format-sub">Styled web sheet with print fonts & margins</span>
                  </div>
                </label>

                <label class="format-radio-label">
                  <input type="radio" name="export-format" value="txt">
                  <div class="format-card">
                    <span class="format-icon">📄</span>
                    <span class="format-name">Plain Text (.txt)</span>
                    <span class="format-sub">UTF-8 clean text file with metadata header</span>
                  </div>
                </label>
              </div>
            </div>

            <div class="form-group">
              <label for="export-note-input" class="form-label">Poet's Note (Optional footnote)</label>
              <input type="text" id="export-note-input" class="form-input" placeholder="e.g. Written on a rainy monsoon evening">
            </div>

            <div class="export-preview-summary">
              <span id="export-lines-summary">Lines to export: 0</span>
            </div>
          </form>
        </div>

        <div class="modal-footer">
          <button type="button" id="btn-print-preview" class="btn-secondary-action">
            🖨 Print / Preview
          </button>
          <button type="button" id="btn-download-export" class="btn-primary-action">
            ⬇ Download File
          </button>
        </div>
      </div>
    `;
  }

  bindEvents() {
    if (!this.modal) return;

    // Close button & backdrop click
    const btnClose = this.modal.querySelector("#btn-close-export-modal");
    if (btnClose) {
      btnClose.addEventListener("click", () => this.close());
    }

    this.modal.addEventListener("click", (e) => {
      if (e.target === this.modal) {
        this.close();
      }
    });

    // Download Button
    const btnDownload = this.modal.querySelector("#btn-download-export");
    if (btnDownload) {
      btnDownload.addEventListener("click", () => this.handleExport(false));
    }

    // Print / Preview Button
    const btnPrint = this.modal.querySelector("#btn-print-preview");
    if (btnPrint) {
      btnPrint.addEventListener("click", () => this.handleExport(true));
    }
  }

  open(data = {}) {
    if (!this.modal) return;

    if (data.lines && Array.isArray(data.lines)) {
      this.currentLines = data.lines;
    } else if (data.stanzas && Array.isArray(data.stanzas)) {
      this.currentLines = data.stanzas.flat().map(l => (typeof l === "string" ? l : l.text));
    } else {
      this.currentLines = [];
    }

    this.currentLanguage = data.language || "hi";
    this.currentTitle = data.title || "मेरी रचना";
    this.currentMeter = data.meter || (this.currentLanguage === "hi" ? "दोहा" : "");

    const titleInput = this.modal.querySelector("#export-title-input");
    if (titleInput) titleInput.value = this.currentTitle;

    const langSelect = this.modal.querySelector("#export-lang-select");
    if (langSelect) langSelect.value = this.currentLanguage;

    const meterInput = this.modal.querySelector("#export-meter-input");
    if (meterInput) meterInput.value = this.currentMeter;

    const summary = this.modal.querySelector("#export-lines-summary");
    if (summary) {
      summary.textContent = `Lines to export: ${this.currentLines.length} (${this.currentLanguage.toUpperCase()})`;
    }

    this.modal.style.display = "flex";
    this.modal.removeAttribute("hidden");
  }

  close() {
    if (!this.modal) return;
    this.modal.style.display = "none";
    this.modal.setAttribute("hidden", "true");
  }

  async handleExport(isPrintPreview = false) {
    if (this.currentLines.length === 0) {
      this.showToast("No lines to export.");
      return;
    }

    const titleInput = this.modal.querySelector("#export-title-input");
    const authorInput = this.modal.querySelector("#export-author-input");
    const langSelect = this.modal.querySelector("#export-lang-select");
    const meterInput = this.modal.querySelector("#export-meter-input");
    const noteInput = this.modal.querySelector("#export-note-input");
    const formatRadio = this.modal.querySelector("input[name='export-format']:checked");

    const format = isPrintPreview ? "html" : (formatRadio?.value || "html");

    const payload = {
      lines: this.currentLines,
      format: format,
      title: titleInput?.value.trim() || "Poem",
      author: authorInput?.value.trim() || "",
      language: langSelect?.value || "hi",
      meter: meterInput?.value.trim() || "",
      author_note: noteInput?.value.trim() || "",
    };

    try {
      const { blob, filename } = await exportPoem(payload);

      if (isPrintPreview) {
        const url = URL.createObjectURL(blob);
        const printWindow = window.open(url, "_blank");
        if (printWindow) {
          printWindow.focus();
        } else {
          this.showToast("Popup blocked. Downloaded file instead.");
          this.triggerDownload(blob, filename);
        }
      } else {
        this.triggerDownload(blob, filename);
        this.showToast(`Exported ${filename} successfully!`);
      }

      this.close();
    } catch (err) {
      this.showToast(`Export error: ${err.message}`);
    }
  }

  triggerDownload(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(() => URL.revokeObjectURL(url), 2000);
  }
}
