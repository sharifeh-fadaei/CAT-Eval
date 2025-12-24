import React, { useState } from 'react';
import axios from 'axios';
import type { ModelOption } from '../App';

type Props = {
  apiBase: string;
  models: ModelOption[];
};

const BatchEvaluationForm: React.FC<Props> = ({ apiBase, models }) => {
  const [selectedModels, setSelectedModels] = useState<string[]>([models[0]?.key ?? '']);
  const [datasetRoot, setDatasetRoot] = useState('');
  const [subsetSelector, setSubsetSelector] = useState('');
  const [batchSize, setBatchSize] = useState(10);
  const [datasetFile, setDatasetFile] = useState<File | null>(null);
  const [outputMode, setOutputMode] = useState<'combined' | 'per-model'>('combined');
  const [status, setStatus] = useState('');
  const [result, setResult] = useState<any>(null);

  const toggleModel = (key: string) => {
    setSelectedModels((prev) =>
      prev.includes(key) ? prev.filter((m) => m !== key) : [...prev, key],
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!datasetFile) {
      setStatus('Attach a .docx or .json dataset file.');
      return;
    }
    if (!subsetSelector.trim()) {
      setStatus('Provide a subset selector (e.g., test_1-test_5,test_7).');
      return;
    }
    setStatus('Submitting batch run...');

    const formData = new FormData();
    formData.append('dataset_file', datasetFile);
    formData.append('dataset_root', datasetRoot);
    formData.append('models', selectedModels.join(','));
    formData.append('subset_selector', subsetSelector);
    formData.append('batch_size', String(batchSize));
    formData.append('output_mode', outputMode);

    try {
      const res = await axios.post(`${apiBase}/api/runs`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setResult(res.data);
      setStatus('Batch evaluation complete');
    } catch (err: any) {
      setStatus(err.response?.data?.detail ?? 'Batch request failed');
    }
  };

  return (
    <div className="card">
      <h2>Mode 2 — Batch Evaluation</h2>
      <p>Submit a dataset file plus image root. HQ-CAT prompt remains fixed for every sample.</p>
      <form onSubmit={handleSubmit}>
        <label>Dataset file (.docx or .json)</label>
        <input type="file" accept=".docx,.json" onChange={(e) => setDatasetFile(e.target.files?.[0] ?? null)} />

        <label>Dataset root (path where sample image folders live)</label>
        <input type="text" value={datasetRoot} onChange={(e) => setDatasetRoot(e.target.value)} placeholder="/path/to/dataset_root" />

        <label>Subset selector</label>
        <input
          type="text"
          value={subsetSelector}
          onChange={(e) => setSubsetSelector(e.target.value)}
          placeholder="test_1-test_5,test_20"
        />

        <label>Batch size</label>
        <input type="number" min={1} value={batchSize} onChange={(e) => setBatchSize(Number(e.target.value))} />

        <label>Models</label>
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          {models.map((m) => (
            <label key={m.key} style={{ fontWeight: 400 }}>
              <input
                type="checkbox"
                checked={selectedModels.includes(m.key)}
                onChange={() => toggleModel(m.key)}
                style={{ marginRight: '6px' }}
              />
              {m.label}
            </label>
          ))}
        </div>

        <label>Output mode</label>
        <select value={outputMode} onChange={(e) => setOutputMode(e.target.value as 'combined' | 'per-model')}>
          <option value="combined">Combined docx</option>
          <option value="per-model">Per-model docx</option>
        </select>

        <button type="submit" className="primary">
          Launch batch run
        </button>
      </form>
      <p className="status">{status}</p>
      {result && (
        <div className="output-block">
          <strong>Run ID:</strong> {result.run_id}
          <br />
          <a href={`${apiBase}/api/runs/${result.run_id}/download`} target="_blank" rel="noreferrer">
            Download run bundle
          </a>
          <pre>{JSON.stringify(result.results, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default BatchEvaluationForm;
