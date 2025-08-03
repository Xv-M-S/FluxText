# download model from huggingface

```bash
huggingface-cli download GD-ML/FLUX-Text --local-dir FLUX-Text --repo-type model
```

# download env from github

## download clip

```bash
git clone https://github.com/openai/CLIP.git
cd CLIP
git checkout dcba3cb2e2827b402d2701e7e1c7d9fed8a20ef1
pip install -e .
```

## download others

```bash
pip install -r new_requirements.txt
```