# Hinglish Mitra

A local Roman-Hindi writing assistant for CS3235. Convert Roman Hindi to Devanagari with AI4Bharat IndicXlit, inspect alternative spellings, edit the draft, and request a Hindi rewrite from BharatGen Param1. Qwen is an additional experimental comparison backend.

## Features

- Roman Hindi to Hindi-script conversion.
- Up to ten candidate spellings for individual words, selected by the user.
- Editable Hindi draft and separate generated suggestion.
- Param1 as the default writing model; Qwen as a labelled comparison option.
- One writing model loaded at a time, with 4-bit quantization.
- Local UTF-8 CSV logging of rewriting inputs, outputs and timings.
- Automated evaluation on 40 fixed cases.

## Architecture

The browser connects to a Gradio app running in Windows. The app requests transliteration from a Flask service in Ubuntu WSL 2 through localhost:8001. IndicXlit runs on CPU in a separate Python 3.10 environment. Param1 or Qwen runs in the Windows Python 3.12 environment on the NVIDIA GPU. Hindi rewriting uses only the editable Hindi draft; adding Roman context performed worse on the development cases.

| Component | Model / software | Execution environment |
|---|---|---|
| Transliteration | AI4Bharat IndicXlit 1.1.3 | WSL 2, Python 3.10.22, CPU |
| Default rewriting | bharatgenai/Param-1-2.9B-Instruct | Windows, Python 3.12, GPU, 4-bit |
| Comparison rewriting | Qwen/Qwen3-4B-Instruct-2507 | Same Windows environment |
| Frontend | Gradio 5.49.1 | Windows, localhost:7860 |
| Local transliteration service | Flask 3.1.2 | WSL, localhost:8001 |

## Hardware used

Lenovo Legion 5 laptop, AMD Ryzen 7 260, 16 GB RAM, NVIDIA GeForce RTX 5050 Laptop GPU with 8 GB VRAM. Model memory use was not measured systematically. Downloaded weights require substantially more disk space than their quantized runtime representation.

## Installation

The application has been exercised in the environments below. The following reconstruction instructions are based on those working package snapshots; a fresh-machine installation has not been independently tested.

Clone or download this repository into `C:\Projects\hinglish-mitra`, or adjust paths below. Install Python 3.12 for Windows, an appropriate NVIDIA driver, and Ubuntu through WSL 2. The exact WSL installation used Python 3.10.22 in an isolated environment; do not use Ubuntu's system Python 3.14 for these older dependencies.

### Windows: frontend and GPU writing models

Run in PowerShell from the repository folder:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install "torch==2.11.0+cu128" --index-url https://download.pytorch.org/whl/cu128
python -m pip install -r requirements-windows.txt
python -m pip check
```

If PowerShell prevents activation, use a Command Prompt terminal and `.venv\Scripts\activate.bat`; avoid changing machine-wide execution policy just for this project.

Verify the GPU and a real calculation:

```powershell
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available()); x=torch.randn(256,256,device='cuda'); print((x @ x).mean().item())"
```

The requirements pin the observed working environment. Some packages in the full snapshot are transitive or leftovers from installation troubleshooting, rather than direct application dependencies.

### Ubuntu WSL: CPU transliteration

In Ubuntu, install build tools:

```bash
sudo apt update
sudo apt install -y build-essential curl
cd /mnt/c/Projects/hinglish-mitra
```

If `uv` is not installed, install it using its official installer:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source "$HOME/.local/bin/env"
```

Create the separate Python environment:

```bash
uv python install 3.10
uv venv --python 3.10 --seed .venv-xlit
source .venv-xlit/bin/activate
```

Prepare the build environment and CPU PyTorch:

```bash
python -m pip install "pip==23.3.2" "setuptools==69.5.1" "wheel==0.43.0" "Cython==0.29.37" "numpy==1.26.4" "cffi==2.1.1"
python -m pip install "torch==2.2.2+cpu" "torchaudio==2.2.2+cpu" --index-url https://download.pytorch.org/whl/cpu
python -m pip install --timeout 300 --retries 10 --no-deps --no-build-isolation -r requirements-xlit.txt
python patch_xlit.py
```

The WSL snapshot intentionally uses `--no-deps`: automatic resolution of IndicXlit/UrduHack dependencies can install unused TensorFlow components and incompatible packages. The snapshot explicitly lists the installed packages used in this Hindi workflow. Build isolation is disabled after installing the known build tools so fairseq uses that environment. Fairseq may compile from source and take several minutes.

Keep pip at 23.3.2 in this environment: old OmegaConf metadata is rejected by newer pip releases. `pip check` in WSL can report missing upstream-declared packages such as Flask-CORS, gevent, pyarrow and UrduHack's ML dependencies. Do not claim a clean full-package dependency check. The Hindi service paths were exercised; unrelated package features are not supported or tested.

The committed requirements replace the original machine-specific `/tmp/fairseq-0.12.2.tar.gz` reference with `fairseq==0.12.2`. Do not commit a requirements file that depends on your own temporary archive location.

### Compatibility patch

`patch_xlit.py` moves the top-level UrduHack normalization import into a function so it is loaded only when requested. It backs up the installed `base_engine.py` before changing it. The patch does not change the model weights or generate fake Urdu normalization results. Urdu functionality remains unvalidated and would need its dependencies.

Run the patch once after a fresh IndicXlit installation. Running it again can report `Expected import not found. No files changed.` because the original import has already been replaced. It must run inside the WSL `.venv-xlit`, not the Windows environment.

### Start the application

Terminal 1, Ubuntu WSL:

```bash
cd /mnt/c/Projects/hinglish-mitra
source .venv-xlit/bin/activate
python xlit_service.py
```

Check http://localhost:8001/health shows `ready` from the Windows browser. WSL localhost forwarding is required; verify this health check before running the frontend.

Terminal 2, Windows PowerShell:

```powershell
cd C:\Projects\hinglish-mitra
.\.venv\Scripts\Activate.ps1
python app.py
```

Open http://localhost:7860. Keep both processes running. The first writing request loads the selected model; changing model selections unloads the old model before loading another. First use downloads several GB of original weights; 4-bit runtime loading does not mean a 4-bit-sized initial download. IndicXlit also downloads its model on first initialization.

Use Ctrl+C in a process's own terminal to stop it. Stop the Windows app before running GPU evaluation scripts to avoid keeping separate models resident in different processes.

### Troubleshooting

- `No module named transformers` under `(.venv-xlit)`: use the Windows `.venv` for app/evaluation, not the IndicXlit environment.
- Cannot reach IndicXlit: check the WSL service and `/health` first.
- Tokenizer or configuration errors: retain Transformers 4.56.2 from the tested snapshot rather than upgrading or downgrading independently.
- A Windows symlink-cache warning does not necessarily prevent loading; it can increase cache disk usage.
- Slow downloads can require retries. Preserve valid cached model files rather than redownloading everything.
- The source uses custom Param1 code through `trust_remote_code=True`; model repository revisions were not pinned in the recorded run, which limits exact future reproducibility.

## Usage

1. Enter Roman Hindi and select Convert to Hindi.
2. Review the editable Hindi draft.
3. If a spelling is wrong, open the candidate panel, look up the Roman word, choose its intended spelling, and copy the incorrect Hindi substring into the replacement field.
4. Apply the selected spelling; the current implementation replaces its first literal occurrence.
5. Select a writing model and request a rewrite.
6. Compare the suggestion against your draft before using it.

Candidate order is not a confidence probability. User-selected correction is not automatic model accuracy. The tool may transliterate English loanwords rather than translate them.

## Evaluation

With the Windows app stopped and the WSL service running:

```powershell
python evaluate.py
```

The runner imports app functions, creates a timestamped results directory, and saves each completed result. It tests 40 automatic conversions and 40 rewrites for each of two models. No manual candidate correction is performed in this evaluation.

| Primary metric | Observed result |
|---|---:|
| Successful conversions | 40/40 |
| Completed rewriting requests | 80/80 |
| Corpus CER | 8.42% |
| Corpus WER | 25.27% |
| Aligned word accuracy | 139/186 (74.73%) |
| Normalized exact sentence matches | 11/40 (27.5%) |
| Mean conversion request time | 2.51 s |
| Mean Param1 generation time | 1.02 s |
| Mean Qwen generation time | 2.75 s |

Aligned word accuracy is the number of exactly matched reference words
divided by the total reference words after minimum-edit-distance word
alignment. Ties favour more exact matches. It uses the same normalization
as CER/WER. This run had 139 matches, 47 substitutions, no deletions and
no insertions across 186 reference words.

CER and WER use Unicode NFC, punctuation replaced by spaces, and collapsed whitespace. Case, spelling and digit script remain distinct. These are single-reference, character-codepoint metrics. Correct alternative spellings may be penalized. A separately labelled decimal-digit-normalization sensitivity analysis gives 6.84% CER, 21.51% WER and 12/40 exact matches. Do not silently substitute sensitivity results for primary results.

Generation times exclude model loading. Attention and caching configurations differ by model; the run is not a controlled speed benchmark. Request success means execution completed, not that the language output was correct.

Writing quality requires review of fluency and meaning separately. The AI-assisted draft review records student corrections for T05, T15 and T31 in both models. The other ratings have not been confirmed, so no final aggregate writing-quality score is claimed.

## Limitations

The system sometimes misreads Roman words, preserves grammatical errors, changes negation or relationships, or rewrites requests as completed actions. Example: an upstream दवा to दावा conversion led to downstream outputs about a claim rather than medicine. Candidate selection helps users inspect alternatives but does not establish reliable automatic correction. Input is limited to 100 words and 2000 characters, with an additional token limit and bounded output generation.

The Flask server and Gradio launch are local development configurations. Windows and WSL must remain running. Rewriting text is saved in local CSV logs; use synthetic examples for the demo and review files before publishing them.

## Sources and attribution

- IndicXlit: https://github.com/AI4Bharat/IndicXlit
- Aksharantar background: https://github.com/AI4Bharat/IndianNLP-Transliteration
- Param1: https://huggingface.co/bharatgenai/Param-1-2.9B-Instruct
- Qwen comparison: https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507

Pretrained weights are used for inference; this project does not train or fine-tune them. The 40 task-specific cases were drafted with AI assistance and supplied for student reference review; they are not sampled benchmark results from Aksharantar. Preserve applicable upstream licenses and verify exact checkpoint license files before distributing model derivatives. No model weights belong in this repository.

## License checks

Checked on 29 October 2026.

| Resource | Published license information |
|---|---|
| AI4Bharat IndicXlit | Official README states that code and models use the MIT License. |
| Qwen3-4B-Instruct-2507 | Official LICENSE file specifies Apache License 2.0. |
| BharatGen Param1-2.9B-Instruct | Model-card metadata specifies Apache 2.0, but its licensing section states MIT. This upstream inconsistency remains unresolved. |

Sources:
- https://github.com/AI4Bharat/IndicXlit#license
- https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507/blob/main/LICENSE
- https://huggingface.co/bharatgenai/Param-1-2.9B-Instruct

The repository contains application code and evaluation results, not
downloaded model weights. Param1 is used for academic experimentation;
its model card identifies research and experimentation as intended uses.