import csv
import gc
import logging
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

import gradio as gr
import requests
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
)

MODELS = {
    "BharatGen Param1": "bharatgenai/Param-1-2.9B-Instruct",
    "Qwen — experimental comparison": "Qwen/Qwen3-4B-Instruct-2507",
}

SERVICE_URL = "http://localhost:8001"

RESULTS_FILE = (
    Path(__file__).resolve().parent / "rewrite_results_hindi_only.csv"
)

logging.basicConfig(level=logging.INFO)
model_lock = threading.Lock()

loaded_model = None
loaded_tokenizer = None
loaded_name = None


def validate_text(text):
    if not isinstance(text, str) or not text.strip():
        raise gr.Error("Please enter some text first.")

    text = text.strip()

    if len(text) > 2000 or len(text.split()) > 100:
        raise gr.Error(
            "Please enter at most 100 words and 2000 characters."
        )

    return text


def load_selected_model(name):
    """Called only while holding model_lock."""
    global loaded_model, loaded_tokenizer, loaded_name

    if name not in MODELS:
        raise gr.Error("Please select a valid model.")

    if loaded_name == name and loaded_model is not None:
        return 0.0

    if not torch.cuda.is_available():
        raise gr.Error(
            "GPU unavailable. Run this app in your Windows .venv."
        )

    print(f"Loading {name}...", flush=True)

    # Release the previous model before loading another.
    loaded_model = None
    loaded_tokenizer = None
    loaded_name = None

    gc.collect()
    torch.cuda.empty_cache()

    started = time.perf_counter()
    model_id = MODELS[name]
    is_param = name == "BharatGen Param1"

    try:
        loaded_tokenizer = AutoTokenizer.from_pretrained(
            model_id,
            trust_remote_code=False,
        )

        loaded_model = AutoModelForCausalLM.from_pretrained(
            model_id,
            trust_remote_code=is_param,
            quantization_config=BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
            ),
            torch_dtype=torch.float16,
            device_map={"": 0},
            attn_implementation="eager" if is_param else "sdpa",
        )

        loaded_model.eval()
        torch.cuda.synchronize()
        loaded_name = name

    except Exception:
        loaded_model = None
        loaded_tokenizer = None
        loaded_name = None

        gc.collect()
        torch.cuda.empty_cache()

        logging.exception("Model loading failed")
        raise gr.Error(
            "Model loading failed. Check the Windows terminal."
        )

    elapsed = time.perf_counter() - started
    print(f"{name} ready in {elapsed:.2f} seconds.", flush=True)

    return elapsed


def convert_to_hindi(text):
    text = validate_text(text)
    started = time.perf_counter()

    try:
        response = requests.post(
            f"{SERVICE_URL}/transliterate",
            json={"text": text},
            timeout=(5, 120),
        )
        response.raise_for_status()
        result = response.json()["text"]

        if not isinstance(result, str) or not result.strip():
            raise ValueError("Invalid transliteration response.")

    except requests.exceptions.Timeout:
        raise gr.Error(
            "IndicXlit timed out. Try a shorter sentence."
        )

    except requests.exceptions.ConnectionError:
        raise gr.Error(
            "Cannot reach IndicXlit. Start xlit_service.py in Ubuntu."
        )

    except Exception:
        logging.exception("Transliteration failed")
        raise gr.Error(
            "Conversion failed. Check the Ubuntu terminal."
        )

    elapsed = time.perf_counter() - started

    return (
        result,
        "",
        f"IndicXlit conversion: {elapsed:.2f} seconds",
    )


def get_spellings(word):
    if not isinstance(word, str):
        raise gr.Error("Enter one Roman Hindi word.")

    word = word.strip()

    if not word or len(word.split()) != 1 or len(word) > 50:
        raise gr.Error(
            "Enter one Roman Hindi word of at most 50 characters."
        )

    try:
        response = requests.post(
            f"{SERVICE_URL}/candidates",
            json={"word": word},
            timeout=(5, 120),
        )
        response.raise_for_status()

        choices = response.json()["candidates"]

        if (
            not isinstance(choices, list)
            or not choices
            or not all(isinstance(choice, str) for choice in choices)
        ):
            raise ValueError("Invalid candidate response.")

    except Exception:
        logging.exception("Candidate lookup failed")
        raise gr.Error(
            "Could not fetch alternatives. Check the Ubuntu service."
        )

    # Require an explicit selection instead of choosing automatically.
    return gr.Dropdown(
        choices=choices,
        value=None,
        interactive=True,
    )


def apply_spelling(text, old_word, selected_word):
    text = validate_text(text)

    if not isinstance(old_word, str) or not old_word.strip():
        raise gr.Error(
            "Copy the incorrect Hindi word from your draft."
        )

    if not selected_word:
        raise gr.Error(
            "Choose the intended spelling from the dropdown."
        )

    old_word = old_word.strip()

    if old_word not in text:
        raise gr.Error(
            "That text was not found in the Hindi draft. "
            "Copy it exactly from the draft."
        )

    corrected = text.replace(old_word, selected_word, 1)

    return (
        corrected,
        "",
        "Applied the selected spelling to the first occurrence. "
        "Review the Hindi draft before requesting a rewrite.",
    )


def save_result(model_name, text, answer, generation_time, load_time):
    needs_header = (
        not RESULTS_FILE.exists()
        or RESULTS_FILE.stat().st_size == 0
    )

    with RESULTS_FILE.open(
        "a",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.writer(file)

        if needs_header:
            writer.writerow(
                [
                    "timestamp_utc",
                    "model",
                    "prompt",
                    "input_hindi",
                    "suggested_hindi",
                    "generation_seconds",
                    "model_load_seconds",
                ]
            )

        writer.writerow(
            [
                datetime.now(timezone.utc).isoformat(),
                model_name,
                "hindi_only",
                text,
                answer,
                round(generation_time, 3),
                round(load_time, 3),
            ]
        )


def comparison_form(text):
    return " ".join(text.split()).rstrip("।.!?")


def improve_hindi(text, selected_model):
    text = validate_text(text)

    if not any("\u0900" <= char <= "\u097f" for char in text):
        raise gr.Error(
            "Convert to Hindi first, or enter Hindi-script text."
        )

    # Hindi-only prompt selected from the development comparison.
    messages = [
        {
            "role": "system",
            "content": (
                "Correct the Hindi text's grammar and spelling. "
                "Preserve meaning, tense, names, dates and numbers. "
                "Do not add facts. Return only the corrected Hindi text."
            ),
        },
        {"role": "user", "content": text},
    ]

    with model_lock:
        load_time = load_selected_model(selected_model)

        inputs = None
        output = None
        generated = None

        try:
            inputs = loaded_tokenizer.apply_chat_template(
                messages,
                tokenize=True,
                add_generation_prompt=True,
                return_dict=True,
                return_tensors="pt",
            ).to("cuda")

            if inputs["input_ids"].shape[-1] > 1024:
                raise gr.Error(
                    "Token limit exceeded. Please shorten the text."
                )

            torch.cuda.synchronize()
            started = time.perf_counter()

            with torch.inference_mode():
                output = loaded_model.generate(
                    **inputs,
                    max_new_tokens=256,
                    do_sample=False,
                    use_cache=selected_model != "BharatGen Param1",
                    pad_token_id=loaded_tokenizer.eos_token_id,
                )

            torch.cuda.synchronize()
            generation_time = time.perf_counter() - started

            generated = output[
                0, inputs["input_ids"].shape[-1]:
            ]

            answer = loaded_tokenizer.decode(
                generated,
                skip_special_tokens=True,
            ).strip()

            reached_limit = len(generated) >= 256

            if not answer:
                raise gr.Error(
                    "The model returned no suggestion."
                )

        except torch.cuda.OutOfMemoryError:
            raise gr.Error(
                "GPU memory is full. Close other GPU-heavy apps "
                "and try shorter text."
            )

        finally:
            inputs = None
            output = None
            generated = None

        unchanged = (
            comparison_form(answer) == comparison_form(text)
        )

        if unchanged:
            verdict = (
                "No substantive edit suggested. "
                "This does not confirm grammatical correctness."
            )
        else:
            verdict = (
                "Rewrite suggested. Check grammar and meaning "
                "before accepting."
            )

        status = (
            f"Model: {selected_model}\n"
            f"Generation: {generation_time:.2f} seconds\n"
            f"Model loading/switching: {load_time:.2f} seconds\n"
            f"{verdict}"
        )

        if reached_limit:
            status += (
                "\nOutput limit reached; the suggestion may be incomplete."
            )

        try:
            save_result(
                selected_model,
                text,
                answer,
                generation_time,
                load_time,
            )
            status += f"\nSaved to {RESULTS_FILE.name}."

        except Exception:
            logging.exception("Could not save result")
            status += (
                "\nCould not save the result. Check the Windows terminal."
            )

    return answer, status


with gr.Blocks(title="Hinglish Mitra") as demo:
    gr.Markdown(
        """
        # Hinglish Mitra

        Convert Roman Hindi into Hindi script, review its spelling,
        and request an AI writing suggestion.

        **Enter → Convert → Review/edit Hindi → Improve**
        """
    )

    roman_input = gr.Textbox(
        label="1. Roman Hindi",
        placeholder="mujhe kal college jana hai",
        lines=3,
    )

    convert_button = gr.Button(
        "Convert to Hindi",
        variant="primary",
    )

    hindi_text = gr.Textbox(
        label="2. Hindi draft — check and edit",
        lines=3,
        interactive=True,
    )

    with gr.Accordion(
        "Fix a transliteration spelling",
        open=False,
    ):
        gr.Markdown(
            """
            Look up a Roman word and choose its intended Hindi spelling.

            Then copy the incorrect text from the Hindi draft below.
            Applying a spelling replaces its **first occurrence only**.
            """
        )

        lookup_word = gr.Textbox(
            label="Roman word to look up",
            placeholder="behen",
        )

        lookup_button = gr.Button(
            "Find alternative spellings"
        )

        spelling_choices = gr.Dropdown(
            choices=[],
            value=None,
            label="Select the intended Hindi spelling",
            interactive=True,
        )

        incorrect_word = gr.Textbox(
            label="Incorrect Hindi text — copy exactly from the draft",
            placeholder="बेहें",
        )

        apply_button = gr.Button(
            "Apply selected spelling"
        )

    model_choice = gr.Dropdown(
        choices=list(MODELS),
        value="BharatGen Param1",
        label="Writing model",
        info=(
            "The model loads when you click Improve. "
            "Only one writing model is loaded at a time."
        ),
    )

    improve_button = gr.Button(
        "Improve Hindi writing",
        variant="primary",
    )

    suggested_text = gr.Textbox(
        label="3. Suggested rewrite — review before using",
        lines=3,
        interactive=False,
    )

    status = gr.Textbox(
        label="Status and timing",
        lines=5,
        interactive=False,
    )

    gr.ClearButton(
        components=[
            roman_input,
            hindi_text,
            lookup_word,
            spelling_choices,
            incorrect_word,
            suggested_text,
            status,
        ],
        value="Clear text",
    )

    gr.Examples(
        examples=[
            ["mujhe kal college jana hai"],
            ["kripya mujhe kal ki meeting ki jankari dein"],
            ["mere behen school jata hai"],
        ],
        inputs=roman_input,
    )

    gr.Markdown(
        """
        **Transliteration:** AI4Bharat IndicXlit  
        **Default writing model:** BharatGen Param1  
        **Experimental comparison:** Qwen

        Alternative spellings require your selection.
        Writing models can miss errors or change meaning.
        Review names, numbers, relationships and negation carefully.

        Rewriting inputs, outputs, model names and timings are saved
        locally in **rewrite_results_hindi_only.csv**.
        """
    )

    convert_button.click(
        fn=convert_to_hindi,
        inputs=roman_input,
        outputs=[hindi_text, suggested_text, status],
        concurrency_limit=1,
    )

    lookup_button.click(
        fn=get_spellings,
        inputs=lookup_word,
        outputs=spelling_choices,
        concurrency_limit=1,
    )

    apply_button.click(
        fn=apply_spelling,
        inputs=[
            hindi_text,
            incorrect_word,
            spelling_choices,
        ],
        outputs=[hindi_text, suggested_text, status],
        concurrency_limit=1,
    )

    improve_button.click(
        fn=improve_hindi,
        inputs=[hindi_text, model_choice],
        outputs=[suggested_text, status],
        concurrency_limit=1,
    )

    model_choice.change(
        fn=lambda: (
            "",
            "Model selection changed. Click Improve to use it.",
        ),
        inputs=None,
        outputs=[suggested_text, status],
        queue=False,
    )


if __name__ == "__main__":
    demo.queue(default_concurrency_limit=1)

    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
    )