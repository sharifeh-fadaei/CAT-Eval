from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class ModelInfo:
    key: str
    label: str
    provider_id: str


class ModelRegistry:
    def __init__(self) -> None:
        self._models: Dict[str, ModelInfo] = {
            "gpt-5.2-pro": ModelInfo("gpt-5.2-pro", "GPT-5.2 Pro", "openai/gpt-5.2-pro"),
            "glm-4.6v": ModelInfo("glm-4.6v", "GLM-4.6V", "z-ai/glm-4.6v"),
            "claude-opus-4.5": ModelInfo("claude-opus-4.5", "Claude Opus 4.5", "anthropic/claude-opus-4.5"),
            "gemini-3-pro": ModelInfo("gemini-3-pro", "Gemini 3 Pro", "google/gemini-3-pro-image-preview"),
            "grok-4.1-fast": ModelInfo("grok-4.1-fast", "Grok 4.1 Fast", "x-ai/grok-4.1-fast"),
        }

    def list_models(self) -> List[ModelInfo]:
        return list(self._models.values())

    def resolve(self, key: str) -> ModelInfo:
        if key not in self._models:
            raise ValueError(f"Unknown model key: {key}")
        return self._models[key]


model_registry = ModelRegistry()
