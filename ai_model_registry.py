import logging
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MODEL_REGISTRY")

class AIModel:
    def __init__(
        self,
        model_id: str,
        name: str,
        description: str,
        task: str,
        source: str,
        size_mb: int,
        license: str,
        status: str = "available"
    ):
        self.model_id = model_id
        self.name = name
        self.description = description
        self.task = task
        self.source = source
        self.size_mb = size_mb
        self.license = license
        self.status = status

    def to_dict(self) -> Dict:
        return {
            "model_id": self.model_id,
            "name": self.name,
            "description": self.description,
            "task": self.task,
            "source": self.source,
            "size_mb": self.size_mb,
            "license": self.license,
            "status": self.status
        }

class ModelRegistry:
    def __init__(self):
        self._models: Dict[str, AIModel] = {}

    def register_model(self, model: AIModel):
        if model.model_id in self._models:
            logger.warning(f"Model already registered: {model.model_id}")
            return
        self._models[model.model_id] = model
        logger.info(f"Registered model: {model.name} ({model.model_id})")

    def remove_model(self, model_id: str):
        if model_id in self._models:
            del self._models[model_id]
            logger.info(f"Removed model: {model_id}")
        else:
            logger.warning(f"Tried to remove unknown model: {model_id}")

    def get_model(self, model_id: str) -> Optional[AIModel]:
        return self._models.get(model_id)

    def list_models(self) -> List[Dict]:
        return [m.to_dict() for m in self._models.values()]

    def mark_unavailable(self, model_id: str):
        if model_id in self._models:
            self._models[model_id].status = "unavailable"
            logger.info(f"Marked model as unavailable: {model_id}")

    def update_model(self, model_id: str, **kwargs):
        model = self._models.get(model_id)
        if not model:
            logger.warning(f"Model not found: {model_id}")
            return

        for key, value in kwargs.items():
            if hasattr(model, key):
                setattr(model, key, value)
                logger.info(f"Updated {key} of model {model_id} to {value}")

if __name__ == "__main__":
    registry = ModelRegistry()

    registry.register_model(AIModel(
        model_id="parallax-llm-v1",
        name="Parallax LLM",
        description="Sentiment classification and crypto intent recognition",
        task="text-classification",
        source="huggingface.co/distilbert-base-uncased",
        size_mb=420,
        license="Apache-2.0"
    ))

    registry.register_model(AIModel(
        model_id="quant-forecast-lite",
        name="Quant Forecast",
        description="Trend prediction based on financial news",
        task="text-forecasting",
        source="hf/quant-bert",
        size_mb=275,
        license="MIT"
    ))

    registry.register_model(AIModel(
        model_id="vision-encoder-v2",
        name="Vision Encoder",
        description="Image-to-text model for captioning crypto charts or logos",
        task="image-captioning",
        source="nlpconnect/vit-gpt2",
        size_mb=680,
        license="CC-BY-SA-4.0"
    ))

    for entry in registry.list_models():
        print(entry)
