"""
model.py
--------
Loads the pretrained google/flan-t5-base model from Hugging Face
Transformers and exposes a single function, generate_text(prompt),
that report_generator.py calls.

We do NOT train anything from scratch — this is a pretrained
instruction-following text-to-text model. We just prompt it.

The model is loaded lazily (only the first time it's needed) and
cached in memory so we don't reload it on every request, which
would be very slow.
"""

import config

_tokenizer = None
_model = None


def _load_model():
    """
    Internal helper. Loads tokenizer + model once and caches them
    in the module-level _tokenizer / _model variables.
    """
    global _tokenizer, _model

    if _model is not None:
        return  # already loaded, nothing to do

    # Imported here (not at top of file) so that the rest of the app
    # (Flask routes, DB, etc.) can be imported/tested without requiring
    # torch/transformers to be installed yet.
    from transformers import T5Tokenizer, T5ForConditionalGeneration

    print(f"[model.py] Loading {config.MODEL_NAME} ... (first request only, please wait)")
    _tokenizer = T5Tokenizer.from_pretrained(config.MODEL_NAME)
    _model = T5ForConditionalGeneration.from_pretrained(config.MODEL_NAME)
    print("[model.py] Model loaded successfully.")


def generate_text(prompt: str, max_new_tokens: int = 512) -> str:
    """
    Given a text prompt, return the model's generated text.
    Used by report_generator.py to turn incident data into a report.
    """
    _load_model()

    inputs = _tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
    output_ids = _model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        num_beams=4,
        no_repeat_ngram_size=3,
        early_stopping=True,
    )
    generated = _tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return generated.strip()
