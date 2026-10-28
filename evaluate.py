import csv
import json
import re
import sys
import time
import unicodedata
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
CASES_FILE = ROOT / "evaluation_cases.csv"


def normalize(text):
    # Ignore punctuation and repeated whitespace for script-conversion
    # metrics. Preserve spelling, case, accents and digits.
    text = unicodedata.normalize("NFC", text)
    text = "".join(
        " " if unicodedata.category(char).startswith("P") else char
        for char in text
    )
    return " ".join(text.split())


def edit_distance(reference, prediction):
    previous = list(range(len(prediction) + 1))

    for i, expected in enumerate(reference, start=1):
        current = [i]

        for j, actual in enumerate(prediction, start=1):
            current.append(
                min(
                    previous[j] + 1,
                    current[j - 1] + 1,
                    previous[j - 1] + (expected != actual),
                )
            )

        previous = current

    return previous[-1]


def extract_seconds(status, label):
    match = re.search(
        re.escape(label) + r":\s*([0-9.]+)\s*seconds",
        status,
    )
    return float(match.group(1)) if match else ""


def main():
    if not CASES_FILE.exists():
        raise SystemExit("evaluation_cases.csv was not found.")

    with CASES_FILE.open(
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        required = {
            "id",
            "category",
            "roman_input",
            "transliteration_reference",
            "writing_reference",
        }

        if not required.issubset(set(reader.fieldnames or [])):
            raise SystemExit(
                "CSV headers do not match the expected five columns."
            )

        cases = list(reader)

    if len(cases) != 40:
        raise SystemExit(
            f"Expected 40 cases, but found {len(cases)}."
        )

    if len({case["id"] for case in cases}) != 40:
        raise SystemExit("Test IDs must be unique.")

    if any(
        not case.get(field, "").strip()
        for case in cases
        for field in required
    ):
        raise SystemExit(
            "Some required cells are empty. Check evaluation_cases.csv."
        )

    # Import the same functions used by the app.
    # Importing app.py does not launch its webpage.
    import app

    import requests

    try:
        health = requests.get(
            f"{app.SERVICE_URL}/health",
            timeout=10,
        )
        health.raise_for_status()
    except requests.RequestException:
        raise SystemExit(
            "IndicXlit is unreachable. Start xlit_service.py in Ubuntu."
        )

    output_dir = ROOT / (
        "evaluation_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    )
    output_dir.mkdir()

    # Preserve the exact test file used in this run.
    (output_dir / CASES_FILE.name).write_bytes(
        CASES_FILE.read_bytes()
    )

    transliteration_file = output_dir / "transliteration_results.csv"
    rewriting_file = output_dir / "rewriting_results.csv"

    predictions = {}

    total_char_edits = 0
    total_reference_chars = 0
    total_word_edits = 0
    total_reference_words = 0
    exact_matches = 0
    successful_conversions = 0
    conversion_times = []

    print("\nPART 1: IndicXlit — 40 cases", flush=True)

    fields = [
        "id",
        "category",
        "roman_input",
        "reference",
        "prediction",
        "character_edits",
        "reference_characters",
        "cer",
        "word_edits",
        "reference_words",
        "wer",
        "normalized_exact_match",
        "seconds",
        "error",
    ]

    with transliteration_file.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()

        for index, case in enumerate(cases, start=1):
            row = {
                "id": case["id"],
                "category": case["category"],
                "roman_input": case["roman_input"],
                "reference": case["transliteration_reference"],
            }

            started = time.perf_counter()

            try:
                prediction, _, _ = app.convert_to_hindi(
                    case["roman_input"]
                )
                elapsed = time.perf_counter() - started
                predictions[case["id"]] = prediction

                reference = normalize(
                    case["transliteration_reference"]
                )
                predicted = normalize(prediction)

                reference_words = reference.split()
                predicted_words = predicted.split()

                char_edits = edit_distance(reference, predicted)
                word_edits = edit_distance(
                    reference_words,
                    predicted_words,
                )

                exact = reference == predicted

                row.update(
                    prediction=prediction,
                    character_edits=char_edits,
                    reference_characters=len(reference),
                    cer=char_edits / max(1, len(reference)),
                    word_edits=word_edits,
                    reference_words=len(reference_words),
                    wer=word_edits / max(1, len(reference_words)),
                    normalized_exact_match=int(exact),
                    seconds=round(elapsed, 3),
                    error="",
                )

                total_char_edits += char_edits
                total_reference_chars += len(reference)
                total_word_edits += word_edits
                total_reference_words += len(reference_words)
                exact_matches += int(exact)
                successful_conversions += 1
                conversion_times.append(elapsed)

                print(
                    f"[{index}/40] {case['id']}: {prediction}",
                    flush=True,
                )

            except Exception as error:
                row["error"] = (
                    f"{type(error).__name__}: {error}"
                )
                print(
                    f"[{index}/40] {case['id']}: FAILED — {error}",
                    flush=True,
                )

            writer.writerow(row)
            file.flush()

    print(
        "\nPART 2: Rewriting — 40 cases per model",
        flush=True,
    )

    fields = [
        "id",
        "category",
        "model",
        "roman_input",
        "actual_transliteration",
        "writing_reference",
        "suggested_rewrite",
        "generation_seconds",
        "model_load_seconds",
        "request_seconds_including_load",
        "status",
        "error",
        "grammar_fluency_1_to_5",
        "meaning_preserved_yes_no",
        "review_notes",
    ]

    rewrite_errors = 0
    completed_rewrites = 0

    with rewriting_file.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()

        # Group by model so it loads once, rather than switching
        # models after every sentence.
        for model_name in app.MODELS:
            print(f"\nModel: {model_name}", flush=True)

            for index, case in enumerate(cases, start=1):
                prediction = predictions.get(case["id"])

                row = {
                    "id": case["id"],
                    "category": case["category"],
                    "model": model_name,
                    "roman_input": case["roman_input"],
                    "actual_transliteration": prediction or "",
                    "writing_reference": case["writing_reference"],
                }

                if prediction is None:
                    row["error"] = (
                        "Skipped because transliteration failed."
                    )
                    rewrite_errors += 1
                else:
                    started = time.perf_counter()

                    try:
                        answer, status = app.improve_hindi(
                            prediction,
                            model_name,
                        )

                        row.update(
                            suggested_rewrite=answer,
                            generation_seconds=extract_seconds(
                                status,
                                "Generation",
                            ),
                            model_load_seconds=extract_seconds(
                                status,
                                "Model loading/switching",
                            ),
                            request_seconds_including_load=round(
                                time.perf_counter() - started,
                                3,
                            ),
                            status=status,
                            error="",
                        )

                        completed_rewrites += 1

                        print(
                            f"[{index}/40] {case['id']}: {answer}",
                            flush=True,
                        )

                    except Exception as error:
                        row["error"] = (
                            f"{type(error).__name__}: {error}"
                        )
                        rewrite_errors += 1

                        print(
                            f"[{index}/40] {case['id']}: "
                            f"FAILED — {error}",
                            flush=True,
                        )

                writer.writerow(row)
                file.flush()

    summary = {
        "test_cases": len(cases),
        "successful_transliterations": successful_conversions,
        "failed_transliterations": (
            len(cases) - successful_conversions
        ),
        "normalization": (
            "Unicode NFC; punctuation replaced with spaces; "
            "whitespace collapsed. Spelling and case preserved."
        ),
        "transliteration_metrics_on_successful_requests": {
            "corpus_CER": (
                total_char_edits / total_reference_chars
                if total_reference_chars else None
            ),
            "corpus_WER": (
                total_word_edits / total_reference_words
                if total_reference_words else None
            ),
            "normalized_exact_matches": exact_matches,
            "normalized_exact_match_rate": (
                exact_matches / successful_conversions
                if successful_conversions else None
            ),
            "mean_request_seconds": (
                sum(conversion_times) / len(conversion_times)
                if conversion_times else None
            ),
        },
        "completed_rewrites": completed_rewrites,
        "failed_or_skipped_rewrites": rewrite_errors,
        "rewriting_quality": "Pending human review.",
        "workflow": (
            "Automatic pipeline: rewriting receives the actual "
            "IndicXlit output, with no manual candidate selection."
        ),
    }

    with (output_dir / "summary.json").open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            summary,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print(f"\nFINISHED. Results folder:\n{output_dir}", flush=True)
    print(
        "\nGrammar and meaning ratings are intentionally blank. "
        "They need human review.",
        flush=True,
    )


if __name__ == "__main__":
    main()