import time
import json
import logging
from typing import Any, Dict
from transformers import pipeline, Pipeline
from pathlib import Path

logger = logging.getLogger("INFERENCE_EXECUTOR")

# Available models and their preloaded pipelines
LOADED_MODELS: Dict[str, Pipeline] = {}

# Default model directory (could be a mounted volume in prod)
MODEL_CACHE = Path("./model_cache")
MODEL_CACHE.mkdir(exist_ok=True)

# Map of known model identifiers to HuggingFace models
MODEL_MAP = {
    "parallax-llm-v1": "distilbert-base-uncased-finetuned-sst-2-english",
    "vision-encoder-v2": "nlpconnect/vit-gpt2-image-captioning",
    "quant-forecast-lite": "mrm8488/bert-tiny-finetuned-financial-news-sentiment"
}


def load_model(model_id: str) -> Pipeline:
    """Dynamically load a model pipeline by ID."""
    if model_id not in MODEL_MAP:
        raise ValueError(f"Unsupported model ID: {model_id}")

    if model_id not in LOADED_MODELS:
        logger.info(f" Loading model pipeline for {model_id}...")
        model_name = MODEL_MAP[model_id]
        try:
            if "vision" in model_id:
                from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
                model = VisionEncoderDecoderModel.from_pretrained(model_name)
                processor = ViTImageProcessor.from_pretrained(model_name)
                tokenizer = AutoTokenizer.from_pretrained(model_name)

                def vision_pipeline(image_input):
                    import requests
                    from PIL import Image
                    img = Image.open(requests.get(image_input, stream=True).raw)
                    pixel_values = processor(images=img, return_tensors="pt").pixel_values
                    output_ids = model.generate(pixel_values)
                    return tokenizer.decode(output_ids[0], skip_special_tokens=True)

                LOADED_MODELS[model_id] = vision_pipeline

            else:
                LOADED_MODELS[model_id] = pipeline("text-classification", model=model_name)
        except Exception as e:
            logger.error(f"Failed to load model {model_id}: {e}")
            raise
    return LOADED_MODELS[model_id]


def run_inference(model_id: str, user_input: str) -> Dict[str, Any]:
    """Executes inference for a given model ID and input text or image."""
    start_time = time.time()

    try:
        model_pipeline = load_model(model_id)
        logger.info(f" Running inference using model '{model_id}'...")

        if callable(model_pipeline) and not isinstance(model_pipeline, Pipeline):
            # For vision models using a custom callable
            output = model_pipeline(user_input)
            result = {"caption": output}
        else:
            output = model_pipeline(user_input)
            result = output[0] if isinstance(output, list) else output

        elapsed = round(time.time() - start_time, 3)
        logger.info(f" Inference complete in {elapsed}s")
        return {
            "model_id": model_id,
            "input": user_input,
            "output": result,
            "latency": elapsed
        }

    except Exception as e:
        logger.error(f" Inference error: {e}")
        return {
            "model_id": model_id,
            "input": user_input,
            "error": str(e),
            "latency": None
        }


if __name__ == "__main__":
    # Example usage
    sample = run_inference("parallax-llm-v1", "Solana is an ultra-fast blockchain.")
    print(json.dumps(sample, indent=2))

    sample2 = run_inference("quant-forecast-lite", "Bitcoin surged 5% today on ETF approval.")
    print(json.dumps(sample2, indent=2))
