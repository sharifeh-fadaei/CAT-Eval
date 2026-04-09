# CAT-Eval: Automatic Evaluator for Chart Alt-Text Quality

This repository contains the code, data, and evaluation results from my master's thesis:

**"Generative AI for High-Quality Alt-Text for Charts: CAT-Eval — Automatic Evaluator for Chart Alt-Text Quality"**

Sharifeh Fadaeijouybari, Universität Trier, 2026.

## What this project does

Charts in scientific papers are often inaccessible to blind and low-vision (BLV) readers because alt text is missing or poorly written. This thesis introduces two things:

1. **HQ-CAT** — a quality framework that defines six factors for scoring chart alt text (Factual Accuracy, Completeness, Context Alignment, Conciseness, Language Quality, and Imaginability), weighted across two dimensions: semantic content (70%) and presentation quality (30%).

2. **CAT-Eval** — a pipeline that uses multimodal LLMs to automatically evaluate chart alt text quality using HQ-CAT. The pipeline takes a chart image, its alt text, the figure caption, and surrounding text from the paper, and produces factor-level scores with diagnostic comments.

Four models were tested: GPT-5.1, Claude Sonnet 4.5, Gemini 3 Pro, and Grok 4. The results were compared against a gold standard of 100 manually annotated samples and validated with a blinded human study.

## Repository Contents

### `data/`
- `gold_standard.xlsx` — The 100 annotated chart–alt text pairs with factor-level scores, diagnostic comments, L1–L4 coverage labels, and overall HQ-CAT scores.
- `few_shot_examples.json` — The five fully worked exemplars used in the few-shot prompt, with complete alt texts, captions, and local texts.

### `prompts/`
- `cat_eval_prompt.txt` — The exact prompt sent to all four models. Includes the system instruction, semantic level definitions, factor weights, JSON output schema, and few-shot exemplar placeholders.

### `results/`
- Raw JSON outputs from each model (one file per model, 100 evaluations each).

### `analysis/`
- Scripts for computing MAE, MSD, signed difference distributions, ANOVA tests, and generating the figures used in the thesis.

### `human_validation/`
- The questionnaire used in the blinded validation study and the participant response data.

### `pipeline/`
- The evaluation script that sends samples to each model via API and collects structured JSON responses.

## How to run the pipeline

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Add your API key for OpenRouter in a `.env` file
4. Run: `python pipeline/run_evaluation.py --model gpt-5.1 --input data/gold_standard.xlsx`

The script sends each sample to the specified model and saves the JSON output to `results/`.

## Key findings

- Three of four models showed systematic leniency (scoring higher than the gold standard). Claude tracked the gold standard most closely but showed errors in both directions.
- Factual Accuracy was the hardest factor for every model, with errors roughly double those on Completeness.
- Six failure patterns were identified, the most important being "Right Diagnosis, Wrong Score" — models could describe quality problems accurately in their comments but did not reflect them in their scores.
- A blinded human validation study confirmed these findings and showed that comprehension errors damage trust more than consistent leniency.

## Citation

If you use HQ-CAT, CAT-Eval, or the gold standard dataset in your work, please cite:

```
Fadaeijouybari, S. (2026). Generative AI for High-Quality Alt-Text for Charts:
CAT-Eval — Automatic Evaluator for Chart Alt-Text Quality.
Master's thesis, Universität Trier.
```

## License

This project is released for research purposes. Please contact the author for commercial use.

## Contact

Sharifeh Fadaeijouybari — S2shfada@uni-trier.de
