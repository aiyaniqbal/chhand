/**
 * API client module for Chhand.
 * Pure fetch wrappers with structured error handling and abort support.
 */

const API_BASE = "/api";

export async function checkHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) {
    throw new Error(`Health check failed: HTTP ${res.status}`);
  }
  return await res.json();
}

export async function analyzePoem(payload, signal = null) {
  const res = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    signal,
  });

  const data = await res.json();
  if (!res.ok) {
    const errorMsg = data?.error?.message || data?.detail || "Failed to analyze meter.";
    throw new Error(errorMsg);
  }
  return data;
}

export async function requestRewrite(payload, signal = null) {
  const res = await fetch(`${API_BASE}/rewrite`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    signal,
  });

  const data = await res.json();
  if (!res.ok) {
    const errorMsg = data?.error?.message || data?.detail?.message || data?.detail || "Failed to generate rewrites.";
    const err = new Error(errorMsg);
    err.code = data?.error?.code || data?.detail?.code;
    throw err;
  }
  return data;
}

export async function findRhymes(word, limit = 10, signal = null) {
  const res = await fetch(`${API_BASE}/rhyme`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ word, limit }),
    signal,
  });

  const data = await res.json();
  if (!res.ok) {
    const errorMsg = data?.error?.message || data?.detail || "Failed to fetch rhymes.";
    throw new Error(errorMsg);
  }
  return data;
}

export async function fetchRhymeFamilies(signal = null) {
  const res = await fetch(`${API_BASE}/rhyme/families`, { signal });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data?.error?.message || data?.detail || "Failed to load rhyme families.");
  }
  return data;
}

/* -------------------------------------------------------------------------
 * Multilingual AI Poetry Studio API Endpoints
 * ------------------------------------------------------------------------- */

export async function fetchLanguages(signal = null) {
  const res = await fetch(`${API_BASE}/languages`, { signal });
  if (!res.ok) {
    throw new Error("Failed to load supported languages.");
  }
  return await res.json();
}

export async function generatePoetry(payload, signal = null) {
  const res = await fetch(`${API_BASE}/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    signal,
  });

  const data = await res.json();
  if (!res.ok) {
    const errorMsg = data?.detail?.message || data?.detail || "Failed to generate poetry.";
    const err = new Error(errorMsg);
    err.code = data?.detail?.code;
    throw err;
  }
  return data;
}

export async function synthesizeSpeech(payload, signal = null) {
  const res = await fetch(`${API_BASE}/tts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    signal,
  });

  if (!res.ok) {
    let errorMsg = "Speech synthesis failed.";
    try {
      const errData = await res.json();
      errorMsg = errData?.detail?.message || errData?.detail || errorMsg;
    } catch (_) {
      errorMsg = `Speech synthesis failed (HTTP ${res.status})`;
    }
    throw new Error(errorMsg);
  }

  return await res.blob();
}

export async function fetchVoices(signal = null) {
  const res = await fetch(`${API_BASE}/tts/voices`, { signal });
  if (!res.ok) {
    return ["Kore", "Puck", "Fenrir", "Aoede", "Charon"];
  }
  return await res.json();
}

export async function fetchStyles(signal = null) {
  const res = await fetch(`${API_BASE}/tts/styles`, { signal });
  if (!res.ok) {
    return [
      "natural poetry recitation",
      "slow meditative reading",
      "dramatic emotional cadence",
      "conversational lyric reading",
    ];
  }
  return await res.json();
}

export async function analyzeUrdu(text, bahrName = "hazaj", signal = null) {
  const res = await fetch(`${API_BASE}/analyze/urdu`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, bahr_name: bahrName }),
    signal,
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data?.detail || "Failed to analyze Urdu verse.");
  }
  return data;
}

export async function analyzeBengali(text, chhandaType = "aksharbritta", signal = null) {
  const res = await fetch(`${API_BASE}/analyze/bengali`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, chhanda_type: chhandaType }),
    signal,
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data?.detail || "Failed to analyze Bengali verse.");
  }
  return data;
}

export async function exportPoem(payload, signal = null) {
  const res = await fetch(`${API_BASE}/export`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    signal,
  });

  if (!res.ok) {
    let errorMsg = "Export failed.";
    try {
      const data = await res.json();
      errorMsg = data?.detail || errorMsg;
    } catch (_) {
      errorMsg = `Export failed (HTTP ${res.status})`;
    }
    throw new Error(errorMsg);
  }

  const blob = await res.blob();
  const disposition = res.headers.get("Content-Disposition") || "";
  let filename = payload.format === "html" ? "poem.html" : "poem.txt";
  const match = disposition.match(/filename="?([^"]+)"?/);
  if (match && match[1]) {
    filename = match[1];
  }

  return { blob, filename };
}
