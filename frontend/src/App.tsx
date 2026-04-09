import React, { useEffect, useState } from 'react';
import axios from 'axios';
import SingleEvaluationForm from './components/SingleEvaluationForm';
import BatchEvaluationForm from './components/BatchEvaluationForm';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export type ModelOption = {
  key: string;
  label: string;
};

// Fallback ONLY (used if backend is unreachable)
const FALLBACK_MODELS: ModelOption[] = [
  { key: 'claude-sonnet-4.5', label: 'Claude Sonnet 4.5' },
  { key: 'gemini-3-pro', label: 'Gemini 3 Pro' },
  { key: 'gpt-5.1', label: 'GPT-5.1' },
  { key: 'grok-4', label: 'Grok 4' },
];

function App() {
  const [page, setPage] = useState<'single' | 'batch'>('single');
  const [backendStatus, setBackendStatus] = useState<string>('');
  const [models, setModels] = useState<ModelOption[]>(FALLBACK_MODELS);

  useEffect(() => {
    // Healthcheck
    axios
      .get(`${API_BASE}/`)
      .then((res) => setBackendStatus(`Backend ready (prompt: ${res.data.prompt})`))
      .catch(() => setBackendStatus('Backend not reachable'));

    // Fetch models dynamically from backend registry
    axios
      .get(`${API_BASE}/api/models`)
      .then((res) => {
        const ms = res.data?.models ?? [];
        const normalized: ModelOption[] = ms
          .map((m: any) => ({ key: String(m.key), label: String(m.label ?? m.key) }))
          .filter((m: ModelOption) => m.key && m.label);

        // Keep only the 4 models you decided (prevents backend drift from re-adding old ones)
        const allow = new Set(['claude-sonnet-4.5', 'gemini-3-pro', 'gpt-5.1', 'grok-4']);
        const filtered = normalized.filter((m) => allow.has(m.key));

        if (filtered.length) setModels(filtered);
      })
      .catch(() => {
        // fallback already set
      });
  }, []);

  return (
    <div className="app-shell">
      <header>
        <h1>HQC-CAT Automatic Alt-Text Evaluator</h1>
        <nav>
          <button
            className={page === 'single' ? 'primary' : 'secondary'}
            onClick={() => setPage('single')}
          >
            Single Evaluation
          </button>
          <button
            className={page === 'batch' ? 'primary' : 'secondary'}
            onClick={() => setPage('batch')}
          >
            Batch Evaluation
          </button>
        </nav>
      </header>

      <p className="status">{backendStatus}</p>

      {page === 'single' ? (
        <SingleEvaluationForm apiBase={API_BASE} models={models} />
      ) : (
        <BatchEvaluationForm apiBase={API_BASE} models={models} />
      )}
    </div>
  );
}

export default App;
