# HQC-CAT Automatic Alt-Text Evaluator for Charts

Research-grade instrument implementing the HQ-CAT v1 evaluator prompt. The system enforces a fixed rubric, semantic-level coverage (L1–L4), strict JSON outputs, and reproducible single/batch workflows.

## Project layout
- `backend/` – FastAPI service. Loads canonical prompt from `backend/app/core/evaluator_prompt/hqcat_v1.txt`.
- `frontend/` – React + Vite UI with Single and Batch evaluation flows.
- `runs/` – persisted run outputs (JSON, docx, zipped bundles).

## Backend setup
1. Install Python 3.11+ and create a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Run the API:
   ```bash
   uvicorn backend.app.main:app --reload --port 8000
   ```
4. Optional: set `OPENROUTER_API_KEY` in a `.env` file to call real models; otherwise a deterministic mock is used.

## Frontend setup
1. Install Node.js (18+ recommended).
2. Install deps and start dev server:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
3. The UI defaults to `http://localhost:8000` for the API. Override with `VITE_API_BASE` if needed.

## Usage
- **Single Evaluation**: upload a chart image plus alt text (caption/local text optional) and choose one model. Download JSON+docx bundle from the UI or `GET /api/single/{run_id}/download`.
- **Batch Evaluation**: upload `.docx` or `.json` dataset plus `dataset_root` where sample image folders live, specify subset selector (ranges/lists), select one or more models, and choose output mode. Download all artifacts from `GET /api/runs/{run_id}/download`.

## Notes
- The evaluator prompt is fixed in `backend/app/core/evaluator_prompt/hqcat_v1.txt` and is never editable via UI.
- Scoring applies the severe factual-accuracy cap (final score ≤ 5 if D1 severity is Severe).
- Dataset parsing supports `sample_name`, `alt_text`, `caption`, `local_text` keys in JSON or colon-prefixed lines in DOCX.
