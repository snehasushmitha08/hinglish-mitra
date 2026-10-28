import csv
import gc
import sys
import time
from pathlib import Path

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUTPUT_FILE = Path(__file__).resolve().parent / "prompt_comparison.csv"

MODELS = [
    ("Param1", "bharatgenai/Param-1-2.9B-Instruct"),
    ("Qwen", "Qwen/Qwen3-4B-Instruct-2507"),
]

# Development examples only, not the final evaluation dataset.
# References are guidance for manual review, not the only valid answers.
CASES = [
    {
        "id": "D1",
        "roman": "mere behen school jata hai",
        "draft": "मेरे बहन स्कूल जाता है",
        "reference": "मेरी बहन स्कूल जाती है।",
        "check": "Correct agreement; preserve sister.",
    },
    {
        "id": "D2",
        "roman": "mere behen school jata hai",
        "draft": "मेरे बेहें स्कूल जाता है",
        "reference": "मेरी बहन स्कूल जाती है।",
        "check": "Recover misspelled sister; do not change relationship.",
    },
    {
        "id": "D3",
        "roman": "mera tabiyat kharab tha isliye main college nahi aaya",
        "draft": "मेरा तबियत खराब था इसलिए मैं कॉलेज नहीं आया",
        "reference": "मेरी तबीयत खराब थी, इसलिए मैं कॉलेज नहीं आया।",
        "check": "Correct agreement; preserve illness and negation.",
    },
    {
        "id": "D4",
        "roman": "bachche maidan mein khel raha hai",
        "draft": "बच्चे मैदान में खेल रहा है",
        "reference": "बच्चे मैदान में खेल रहे हैं।",
        "check": "Correct plural agreement.",
    },
    {
        "id": "D5",
        "roman": "kripya mujhe kal ki baithak ka samay batayein",
        "draft": "कृपया मुझे कल की बैठक का समय बताएं।",
        "reference": "कृपया मुझे कल की बैठक का समय बताएं।",
        "check": "Preserve an already reasonable request.",
    },
    {
        "id": "D6",
        "roman": "reena ne 15 october ko 250 rupaye diye",
        "draft": "रीना ने 15 अक्टूबर को 250 रुपये दिए।",
        "reference": "रीना ने 15 अक्टूबर को 250 रुपये दिए।",
        "check": "Preserve name, date, amount and meaning.",
    },
]

BASE_INSTRUCTION = (
    "Correct the Hindi text's grammar and spelling. "
    "Preserve meaning, tense, names, dates and numbers. "
    "Do not add facts. Return only the corrected Hindi text."
)

FIELDS = [
    "model",
    "prompt",
    "case_id",
    "roman",
    "hindi_draft",
    "reference_for_review",
    "review_check",
    "output",
    "generation_seconds",
    "output_limit_reached",
    "error",
    "grammar_pass",
    "meaning_preserved",
    "review_notes",
]


def make_messages(case, prompt_name):
    if prompt_name == "hindi_only":
        return [
            {"role": "system", "content": BASE_INSTRUCTION},
            {"role": "user", "content": case["draft"]},
        ]

    return [
        {
            "role": "system",
            "content": (
                BASE_INSTRUCTION
                + " Use the original Roman Hindi to interpret unclear "
                "or misspelled words. The Hindi draft takes priority "
                "when it clearly differs from the original. "
                "Preserve subjects, relationships and negation."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Original Roman Hindi:\n{case['roman']}\n\n"
                f"Hindi draft:\n{case['draft']}\n\n"
                "Corrected Hindi:"
            ),
        },
    ]


def test_model(model_name, model_id, writer, file):
    is_param = model_name == "Param1"

    print(f"\nLoading {model_name}...", flush=True)

    tokenizer = AutoTokenizer.from_pretrained(
        model_id,
        trust_remote_code=False,
    )

    model = AutoModelForCausalLM.from_pretrained(
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
    model.eval()

    try:
        for prompt_name in ["hindi_only", "roman_context"]:
            for case in CASES:
                row = {
                    "model": model_name,
                    "prompt": prompt_name,
                    "case_id": case["id"],
                    "roman": case["roman"],
                    "hindi_draft": case["draft"],
                    "reference_for_review": case["reference"],
                    "review_check": case["check"],
                }

                inputs = None
                output = None

                try:
                    inputs = tokenizer.apply_chat_template(
                        make_messages(case, prompt_name),
                        tokenize=True,
                        add_generation_prompt=True,
                        return_dict=True,
                        return_tensors="pt",
                    ).to("cuda")

                    torch.cuda.synchronize()
                    started = time.perf_counter()

                    with torch.inference_mode():
                        output = model.generate(
                            **inputs,
                            max_new_tokens=128,
                            do_sample=False,
                            use_cache=not is_param,
                            pad_token_id=tokenizer.eos_token_id,
                        )

                    torch.cuda.synchronize()
                    elapsed = time.perf_counter() - started

                    tokens = output[
                        0, inputs["input_ids"].shape[-1]:
                    ]

                    answer = tokenizer.decode(
                        tokens,
                        skip_special_tokens=True,
                    ).strip()

                    row.update(
                        output=answer,
                        generation_seconds=round(elapsed, 3),
                        output_limit_reached=len(tokens) >= 128,
                        error="",
                    )

                    print(
                        f"\n{model_name} | {prompt_name} | {case['id']}"
                        f"\nInput:  {case['draft']}"
                        f"\nOutput: {answer}"
                        f"\nTime: {elapsed:.2f}s",
                        flush=True,
                    )

                except Exception as error:
                    row["error"] = (
                        f"{type(error).__name__}: {error}"
                    )
                    print(
                        f"\nFailed: {model_name}, "
                        f"{prompt_name}, {case['id']}: {error}",
                        flush=True,
                    )

                finally:
                    inputs = None
                    output = None
                    # Remove the view into the generated GPU tensor.
                    if "tokens" in locals():
                        del tokens

                writer.writerow(row)
                file.flush()

    finally:
        del model
        del tokenizer


def main():
    if not torch.cuda.is_available():
        raise SystemExit(
            "GPU unavailable. Run this in Windows .venv."
        )

    if OUTPUT_FILE.exists():
        raise SystemExit(
            "prompt_comparison.csv already exists. "
            "Rename it before running again to preserve its results."
        )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        file.flush()

        for model_name, model_id in MODELS:
            try:
                test_model(model_name, model_id, writer, file)
            finally:
                gc.collect()
                torch.cuda.empty_cache()

    print(f"\nFinished. Results saved to:\n{OUTPUT_FILE}")


if __name__ == "__main__":
    main()