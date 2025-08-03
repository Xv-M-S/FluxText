# download model from huggingface

```bash
huggingface-cli download GD-ML/FLUX-Text --local-dir FLUX-Text --repo-type model
```

# download env from github

## download clip

```bash
# Create a new conda environment
conda create -n flux_text python=3.10
conda activate flux_text

git clone https://github.com/openai/CLIP.git
cd CLIP
git checkout dcba3cb2e2827b402d2701e7e1c7d9fed8a20ef1
pip install -e .

# Install other dependencies
pip install -r new_requirements.txt
pip install flash_attn --no-build-isolation
pip install Pillow==9.5.0
```

## download others

```bash
pip install -r new_requirements.txt
```