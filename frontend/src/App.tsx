import React, { useMemo, useState } from 'react';
import axios from 'axios';
import SingleEvaluationForm from './components/SingleEvaluationForm';
import BatchEvaluationForm from './components/BatchEvaluationForm';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export type ModelOption = {
  key: string;
  label: string;
};

const MODELS: ModelOption[] = [
  { key: 'gpt-5.2-pro', label: 'GPT-5.2 Pro' },
  { key: 'glm-4.6v', label: 'GLM-4.6V' },
  { key: 'claude-opus-4.5', label: 'Claude Opus 4.5' },
  { key: 'gemini-3-pro', label: 'Gemini 3 Pro' },
  { key: 'grok-4.1-fast', label: 'Grok 4.1 Fast' },
];

function App() {
  const [page, setPage] = useState<'single' | 'batch'>('single');
  const [backendStatus, setBackendStatus] = useState<string>('');

  React.useEffect(() => {
    axios
      .get(`${API_BASE}/`)
      .then((res) => setBackendStatus(`Backend ready (prompt: ${res.data.prompt})`))
      .catch(() => setBackendStatus('Backend not reachable'));
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
        <SingleEvaluationForm apiBase={API_BASE} models={MODELS} />
      ) : (
        <BatchEvaluationForm apiBase={API_BASE} models={MODELS} />
      )}
    </div>
  );
}

export default App;
