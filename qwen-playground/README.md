# Local LLM Playground

## Model used: Qwen 7.5B

This project is a **local AI/ML playground** focused on:
- Running **LLMs locally**
- Experimenting with **prompts, notebooks, and small pipelines**
- Avoiding cloud dependencies whenever possible

---


## Environment Setup

### 1. Create & activate virtual environment
From the project root:

```bash
uv venv -p python
source .venv/bin/activate
```

### 2. Install deps
```bash
uv sync
```

### 3. Ollama Setup (Local LLM Runtime)

I am doing this on arch, so here's a note for me:

```bash
sudo pacman -S ollama
sudo systemctl enable --now ollama
```

Pull and run the model:
```bash
ollama pull qwen2.5:7b
ollama run qwen2.5:7b
```


