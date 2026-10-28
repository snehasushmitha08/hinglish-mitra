import torch
from flask import Flask, request, jsonify
from ai4bharat.transliteration import XlitEngine

# Limit CPU usage for this small local service.
torch.set_num_threads(2)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16_000

print("Loading IndicXlit...", flush=True)
engine = XlitEngine("hi", beam_width=10, rescore=False)
print("IndicXlit ready.", flush=True)


@app.get("/health")
def health():
    return jsonify(status="ready", model="IndicXlit", language="Hindi")


@app.post("/transliterate")
def transliterate():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(error="Expected a JSON object."), 400

    text = data.get("text")

    if not isinstance(text, str) or not text.strip():
        return jsonify(error="Please enter some text."), 400

    if len(text) > 2000 or len(text.split()) > 100:
        return jsonify(error="Please enter at most 100 words and 2000 characters."), 400

    try:
        result = engine.translit_sentence(text.strip(), lang_code="hi")
        return jsonify(text=result)
    except Exception:
        app.logger.exception("Transliteration failed")
        return jsonify(error="Transliteration failed. Check the Ubuntu terminal."), 500

@app.post("/candidates")
def candidates():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(error="Expected a JSON object."), 400

    word = data.get("word")

    if (
        not isinstance(word, str)
        or not word.strip()
        or len(word) > 50
        or len(word.split()) != 1
    ):
        return jsonify(error="Enter one Roman Hindi word."), 400

    try:
        result = engine.translit_word(
            word.strip(),
            lang_code="hi",
            topk=10,
        )

        # Support either a language-keyed response or a list.
        choices = result.get("hi", []) if isinstance(result, dict) else result

        if not isinstance(choices, list):
            raise ValueError("Unexpected candidate response.")

        return jsonify(candidates=choices)

    except Exception:
        app.logger.exception("Candidate lookup failed")
        return jsonify(error="Could not retrieve spellings."), 500


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=8001,
        debug=False,
        threaded=False,
    )