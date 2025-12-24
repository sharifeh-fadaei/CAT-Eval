from __future__ import annotations

import asyncio
import json
import shutil
from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from .config import get_settings
from .docx_parser import DocxParser
from .evaluator import evaluate_sample
from .image_finder import find_image, ImageNotFound
from .json_parser import JsonParser
from .model_registry import model_registry
from .output_docx_writer import write_batch_docx, write_combined_docx, write_single_docx
from .output_json_writer import write_batch_json, write_single_json
from .run_manager import run_manager
from .sample_selector import parse_selector, validate_samples


app = FastAPI(title="HQC-CAT Automatic Alt-Text Evaluator for Charts")
settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def chunked(iterable: List[Any], n: int) -> List[List[Any]]:
    return [iterable[i : i + n] for i in range(0, len(iterable), n)]


@app.get("/api/models")
async def list_models():
    return {"models": [m.__dict__ for m in model_registry.list_models()]}


@app.post("/api/single/evaluate")
async def single_evaluate(
    image: UploadFile = File(...),
    alt_text: str = Form(...),
    caption: str | None = Form(None),
    local_text: str | None = Form(None),
    model_key: str = Form(...),
):
    if not alt_text:
        raise HTTPException(status_code=400, detail="alt_text is required")
    run_id = run_manager.create_run({"mode": "single", "model": model_key})
    image_bytes = await image.read()
    try:
        result = await evaluate_sample(
            image_bytes=image_bytes,
            image_filename=image.filename,
            sample_name="single_sample",
            alt_text=alt_text,
            caption=caption,
            local_text=local_text,
            model_key=model_key,
        )
    except Exception as exc:  # noqa: BLE001
        run_manager.update_status(run_id, "failed", {"error": str(exc)})
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    run_dir = settings.run_root / run_id
    json_path = write_single_json(run_dir, run_id, result)
    docx_path = write_single_docx(run_dir, run_id, result)
    run_manager.update_status(run_id, "completed", {"outputs": [str(json_path), str(docx_path)]})
    return {"run_id": run_id, "result": result, "outputs": {"json": str(json_path), "docx": str(docx_path)}}


@app.get("/api/single/{run_id}/download")
async def download_single(run_id: str):
    run_dir = settings.run_root / run_id
    if not run_dir.exists():
        raise HTTPException(status_code=404, detail="run not found")
    archive_path = shutil.make_archive(str(run_dir / "bundle"), "zip", run_dir)
    return FileResponse(archive_path, filename=f"single_{run_id}.zip")


@app.post("/api/runs")
async def create_batch_run(
    dataset_file: UploadFile = File(...),
    dataset_root: str = Form(...),
    models: str = Form(...),
    subset_selector: str = Form(...),
    batch_size: int = Form(10),
    output_mode: str = Form("combined"),
):
    if not Path(dataset_root).exists():
        raise HTTPException(status_code=400, detail="dataset_root does not exist")
    try:
        model_keys = [m.strip() for m in models.split(",") if m.strip()]
        for key in model_keys:
            model_registry.resolve(key)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    run_id = run_manager.create_run(
        {
            "mode": "batch",
            "models": model_keys,
            "dataset_root": dataset_root,
            "subset_selector": subset_selector,
            "batch_size": batch_size,
            "output_mode": output_mode,
        }
    )
    run_dir = settings.run_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    dataset_path = run_dir / dataset_file.filename
    dataset_path.write_bytes(await dataset_file.read())

    try:
        samples = parse_dataset(dataset_path)
        requested_samples = parse_selector(subset_selector)
        available_names = [s.get("sample_name") for s in samples]
        validate_samples(requested_samples, available_names)
        filtered_samples = [s for s in samples if s.get("sample_name") in requested_samples]
        for sample in filtered_samples:
            if not sample.get("alt_text"):
                raise HTTPException(status_code=400, detail=f"alt_text missing for {sample.get('sample_name')}")
        results_by_model: Dict[str, List[Dict[str, Any]]] = {}
        for model_key in model_keys:
            model_records: List[Dict[str, Any]] = []
            for batch_index, sample_batch in enumerate(chunked(filtered_samples, batch_size)):
                batch_records: List[Dict[str, Any]] = []
                for sample in sample_batch:
                    image_path = find_image(Path(dataset_root), sample["sample_name"])
                    image_bytes = image_path.read_bytes()
                    result = await evaluate_sample(
                        image_bytes=image_bytes,
                        image_filename=image_path.name,
                        sample_name=sample["sample_name"],
                        alt_text=sample.get("alt_text", ""),
                        caption=sample.get("caption"),
                        local_text=sample.get("local_text"),
                        model_key=model_key,
                    )
                    batch_records.append(result)
                    model_records.append(result)
                write_batch_json(run_dir, run_id, model_key, batch_index, batch_records)
            write_batch_docx(run_dir, run_id, model_key, model_records)
            results_by_model[model_key] = model_records

        if output_mode == "combined":
            write_combined_docx(run_dir, run_id, results_by_model)

        run_manager.update_status(run_id, "completed", {"results": results_by_model})
        return {"run_id": run_id, "results": results_by_model}
    except (ImageNotFound, Exception) as exc:  # noqa: BLE001
        run_manager.update_status(run_id, "failed", {"error": str(exc)})
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/runs/{run_id}")
async def get_run(run_id: str):
    try:
        metadata = run_manager.get_metadata(run_id)
        return metadata
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="run not found") from None


@app.get("/api/runs/{run_id}/results")
async def get_run_results(run_id: str):
    run_dir = settings.run_root / run_id
    if not run_dir.exists():
        raise HTTPException(status_code=404, detail="run not found")
    json_files = list(run_dir.glob("*.json"))
    results: Dict[str, Any] = {}
    for path in json_files:
        try:
            content = json.loads(path.read_text(encoding="utf-8"))
            results[path.name] = content
        except json.JSONDecodeError:
            continue
    return JSONResponse(results)


@app.get("/api/runs/{run_id}/download")
async def download_run(run_id: str):
    run_dir = settings.run_root / run_id
    if not run_dir.exists():
        raise HTTPException(status_code=404, detail="run not found")
    archive_path = shutil.make_archive(str(run_dir / "bundle"), "zip", run_dir)
    return FileResponse(archive_path, filename=f"run_{run_id}.zip")


@app.post("/api/runs/{run_id}/cancel")
async def cancel_run(run_id: str):
    try:
        run_manager.update_status(run_id, "cancelled")
        return {"run_id": run_id, "status": "cancelled"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="run not found") from None


def parse_dataset(dataset_path: Path) -> List[Dict[str, Any]]:
    ext = dataset_path.suffix.lower()
    if ext == ".docx":
        return DocxParser(dataset_path).parse()
    if ext == ".json":
        return JsonParser(dataset_path).parse()
    raise HTTPException(status_code=400, detail="Unsupported dataset format; use .docx or .json")


@app.get("/")
async def healthcheck():
    return {"status": "ok", "prompt": str(settings.evaluator_prompt_path)}
