# Hinglish Mitra

**Turn Hindi typed in English letters into Hindi script, then refine the wording.**

Hinglish Mitra is a local writing assistant built with AI4Bharat IndicXlit and BharatGen Param1. It combines script conversion, alternative word spellings, an editable draft, and AI rewriting in one interface. Qwen is available as an experimental comparison model.

For example, `mujhe paani chahiye` becomes `मुझे पानी चाहिए`. This is **transliteration**: the language stays Hindi while the script changes. Rewriting is a separate step that can suggest grammar and phrasing changes.

## What it does

- **Convert:** turn Roman Hindi into Hindi script, including text with English loanwords.
- **Choose spellings:** inspect up to ten alternatives for a word when the first conversion is wrong.
- **Edit:** correct the Hindi draft directly before requesting a rewrite.
- **Compare:** switch between Param1 and Qwen, with the draft and suggestion kept separate.
- **Evaluate:** run a fixed 40-case test set and export outputs, errors, and timings.

English translation is not included. Writing suggestions can be wrong, so the final wording remains the user's decision.

## How it works

| Component | Role | Runs on |
|---|---|---|
| [IndicXlit](https://github.com/AI4Bharat/IndicXlit) | Script conversion and spelling candidates | CPU in Ubuntu WSL 2 |
| [Param1 2.9B Instruct](https://huggingface.co/bharatgenai/Param-1-2.9B-Instruct) | Default Hindi rewriting model | NVIDIA GPU on Windows |
| [Qwen3-4B-Instruct-2507](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507) | Experimental rewriting comparison | Same GPU, loaded separately |
| Gradio + Flask | Browser interface and local conversion service | Windows + WSL |

The Windows app calls the WSL service over localhost. Both writing models use 4-bit NF4 quantization; only one is loaded at a time. All models are pretrained—no training or fine-tuning is performed.

Separate Python environments accommodate IndicXlit's older dependencies alongside the newer GPU stack. The final rewriting prompt uses the Hindi draft alone, selected after a small development comparison with Roman-context prompting.

## Getting started

**Tested setup:** Windows 11, Ubuntu WSL 2, 16 GB RAM, and an RTX 5050 Laptop GPU with 8 GB VRAM. This is the tested configuration, not a measured minimum. Install Python 3.12 on Windows and a compatible NVIDIA driver. Initial model downloads need internet and several GB of disk space.

Download or clone the repository into `C:\Projects\hinglish-mitra`, or adjust the paths below. Installation instructions reflect the working environment; clean-machine reproduction has not been independently verified.

<details>
<summary><strong>1. Set up the Windows environment</strong></summary>

Run in PowerShell:

```powershell
cd C:\Projects\hinglish-mitra
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install "torch==2.11.0+cu128" --index-url https://download.pytorch.org/whl/cu128
python -m pip install -r requirements-windows.txt
```

If activation is blocked in PowerShell, use Command Prompt and `.venv\Scripts\activate.bat`.

</details>

<details>
<summary><strong>2. Set up the Ubuntu WSL environment</strong></summary>

In Ubuntu:

```bash
sudo apt update
sudo apt install -y build-essential curl
cd /mnt/c/Projects/hinglish-mitra
```

Install [uv](https://docs.astral.sh/uv/) if needed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source "$HOME/.local/bin/env"
```

Create a Python 3.10 environment and install the pinned dependencies:

```bash
uv python install 3.10
uv venv --python 3.10 --seed .venv-xlit
source .venv-xlit/bin/activate
python -m pip install "pip==23.3.2" "setuptools==69.5.1" "wheel==0.43.0" "Cython==0.29.37" "numpy==1.26.4" "cffi==2.1.1"
python -m pip install "torch==2.2.2+cpu" "torchaudio==2.2.2+cpu" --index-url https://download.pytorch.org/whl/cpu
python -m pip install --timeout 300 --retries 10 --no-deps --no-build-isolation -r requirements-xlit.txt
python patch_xlit.py
```

Keep the pinned pip version: newer releases reject old OmegaConf metadata. `--no-deps` intentionally avoids unused upstream dependencies. Consequently, WSL's `pip check` can report omissions; only the Hindi paths used here have been validated.

`patch_xlit.py` defers an UrduHack import so unused TensorFlow components do not block Hindi processing. It backs up the original installed file and should be applied once after installation. It does not alter model weights. Urdu support is not validated.

</details>

### Start the app

**Terminal 1 — Ubuntu WSL:**

```bash
cd /mnt/c/Projects/hinglish-mitra
source .venv-xlit/bin/activate
python xlit_service.py
```

Check that [the service health endpoint](http://localhost:8001/health) shows `ready` from Windows.

**Terminal 2 — Windows PowerShell:**

```powershell
cd C:\Projects\hinglish-mitra
.\.venv\Scripts\Activate.ps1
python app.py
```

Open **[localhost:7860](http://localhost:7860)** and keep both processes running. The first rewrite loads the selected model; switching models takes additional time.

## Using the assistant

1. Enter Roman Hindi and click **Convert to Hindi**.
2. Review the Hindi draft. Edit it directly or open **Fix a transliteration spelling** to look up alternatives.
3. Select the intended spelling, copy the incorrect Hindi text from the draft, and apply the replacement. Only the first matching occurrence is replaced.
4. Select a writing model and click **Improve Hindi writing**.
5. Compare the suggestion with the draft, especially names, numbers, negation, and relationships.

Inputs are limited to 100 words and 2000 characters, with additional token limits. Rewriting inputs, outputs, model names, and timings are saved locally in `rewrite_results_hindi_only.csv`.

## Evaluation

The custom test set contains **40 cases** covering everyday sentences, grammar errors, Hindi-English mixing, and preservation of names, numbers, dates, and negation. Cases were drafted with AI assistance and supplied for student reference review; they were not sampled from Aksharantar.

| Conversion metric | Result |
|---|---:|
| Character Error Rate | **8.42%** |
| Word Error Rate | **25.27%** |
| Aligned word accuracy | **74.73%** — 139/186 words |
| Exact sentence matches after normalization | **27.5%** — 11/40 cases |

All 40 conversions and 80 rewriting requests completed. Mean conversion time was **2.51 s**; mean generation time was **1.02 s** for Param1 and **2.75 s** for Qwen. Loading time is excluded, and model settings differ, so these are observed timings rather than a controlled speed benchmark.

Metrics use Unicode NFC, punctuation-to-space replacement, and collapsed whitespace. Word accuracy counts exact matches after minimum-edit-distance alignment, favouring more matches in ties: 139 matches and 47 substitutions, with no insertions or deletions. Single references can penalize valid spelling and digit-script alternatives.

### Reproduce the evaluation

Keep the WSL service running, stop the Windows app to release GPU memory, and run in the Windows environment:

```powershell
python evaluate.py
```

Results are saved in a timestamped folder. Each writing model receives the actual IndicXlit output; manual spelling corrections are excluded. [Recorded results](evaluation_20261029_013004_568731/) include raw outputs and metrics. [Development experiments](prompt_comparison.csv) are separate from this final set.

Conversion scores do not measure rewriting quality. The [AI-assisted writing review](AI_assisted_evaluation_review.md) assesses grammar and meaning separately; only the student corrections explicitly recorded there are confirmed.

## Known limitations

Incorrect conversion can propagate into rewriting. In one evaluated case, **दवा** (medicine) became **दावा** (claim), and the writing models continued with the wrong meaning. Models also retained grammatical errors, introduced negation, or changed requests into completed actions.

Spelling alternatives provide a user-assisted recovery mechanism, not guaranteed automatic correction. The application is intended for reviewed writing suggestions, and its 40-case evaluation does not establish reliability across all Hindi usage. Model revisions were not pinned in the recorded run, limiting exact future reproducibility.

## Model licenses

Checked on 29 October 2026:

- **IndicXlit:** its [official README](https://github.com/AI4Bharat/IndicXlit#license) states that code and models use MIT.
- **Qwen:** its [LICENSE](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507/blob/main/LICENSE) specifies Apache 2.0.
- **Param1:** its [model card](https://huggingface.co/bharatgenai/Param-1-2.9B-Instruct) lists Apache 2.0 in metadata but MIT in the licensing section. This upstream inconsistency remains unresolved; stated intended uses include research and experimentation.

Model weights are downloaded from their publishers and are not included in this repository.
