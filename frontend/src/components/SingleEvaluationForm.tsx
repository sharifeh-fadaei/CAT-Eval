import React, { useState } from 'react';
import axios from 'axios';
import type { ModelOption } from '../App';

type Props = {
  apiBase: string;
  models: ModelOption[];
};

const SingleEvaluationForm: React.FC<Props> = ({ apiBase, models }) => {
  const [model, setModel] = useState(models[0]?.key ?? '');
  const [altText, setAltText] = useState('');
  const [caption, setCaption] = useState('');
  const [localText, setLocalText] = useState('');
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [status, setStatus] = useState('');
  const [result, setResult] = useState<any>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!imageFile) {
      setStatus('Please upload a chart image.');
      return;
    }
    setStatus('Submitting to evaluator...');
    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('alt_text', altText);
    formData.append('caption', caption);
    formData.append('local_text', localText);
    formData.append('model_key', model);

    try {
      const res = await axios.post(`${apiBase}/api/single/evaluate`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setResult(res.data);
      setStatus('Evaluation complete');
    } catch (err: any) {
      setStatus(err.response?.data?.detail ?? 'Request failed');
    }
  };

  return (
    <div className="card">
      <h2>Mode 1 — Single Sample Evaluation</h2>
      <p>Upload one chart and alt text. The HQ-CAT prompt is fixed and enforced server-side.</p>
      <form onSubmit={handleSubmit}>
        <label>Chart image (png/jpg/jpeg/webp)</label>
        <input type="file" accept="image/*" onChange={(e) => setImageFile(e.target.files?.[0] ?? null)} />

        <label>Alt text (required)</label>
        <textarea required value={altText} onChange={(e) => setAltText(e.target.value)} placeholder="Describe the chart..." />

        <label>Caption (optional)</label>
        <textarea value={caption} onChange={(e) => setCaption(e.target.value)} />

        <label>Local text (optional)</label>
        <textarea value={localText} onChange={(e) => setLocalText(e.target.value)} />

        <label>Model</label>
        <select value={model} onChange={(e) => setModel(e.target.value)}>
          {models.map((m) => (
            <option key={m.key} value={m.key}>
              {m.label}
            </option>
          ))}
        </select>

        <button type="submit" className="primary">
          Evaluate
        </button>
      </form>
      <p className="status">{status}</p>
      {result && (
        <div className="output-block">
          <strong>Run ID:</strong> {result.run_id}
          <br />
          <a href={`${apiBase}/api/single/${result.run_id}/download`} target="_blank" rel="noreferrer">
            Download bundle
          </a>
          <pre>{JSON.stringify(result.result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default SingleEvaluationForm;
