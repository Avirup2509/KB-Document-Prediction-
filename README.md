# 🧠 KB Intelligence Hub

AI-powered Knowledge Base article prediction and incident resolution tool built with **Streamlit**, **LangChain**, and **Ollama (LLMA)**.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🚨 **Incident Analyzer** | AI analysis of incidents with suggested owners, resolution steps, and auto-generated KB draft |
| 📚 **KB Article Generator** | Create ITIL-aligned KB articles from any topic or problem description |
| 📋 **SOP Builder** | Generate enterprise-grade Standard Operating Procedures |
| 🔧 **Troubleshooting Guide** | Create decision-tree based troubleshooting guides |
| 🔮 **KB Gap Predictor** | Predict which KB articles your team should create next based on incident patterns |

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.9+
- [Ollama](https://ollama.ai) installed and running
- A compatible LLM model pulled in Ollama

### 2. Install Ollama & Pull a Model

```bash
# Install Ollama (Linux/Mac)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model (choose one)
ollama pull llama3.2       # Recommended - fast & capable
ollama pull llama3.1       # Larger, more detailed
ollama pull mistral        # Good alternative
ollama pull mixtral        # Best quality, requires more RAM

# Start Ollama
ollama serve
```

### 3. Install Python Dependencies

```bash
cd kb_predictor
pip install -r requirements.txt
```

### 4. Run the App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## ⚙️ Configuration

In the **sidebar**:
- **Ollama URL**: Default is `http://localhost:11434`
- **Model**: Select from available models
- **Temperature**: Lower (0.1-0.3) for consistent/factual output; Higher (0.6-0.9) for creative content
- **Max Tokens**: Controls response length (2048 recommended)

---

## 📖 Usage Guide

### 🚨 Incident Analyzer
1. Enter incident title and description
2. Set severity and affected system
3. Click **Analyze Incident**
4. Review: AI-suggested owner, resolution steps, estimated time
5. Save the auto-generated KB article draft

### 📚 KB Article Generator
1. Enter a topic/problem statement
2. Select category, audience, and style
3. Click **Generate KB Article**
4. Edit and download the article in Markdown format

### 📋 SOP Builder
1. Name your process and select department
2. Fill in objective and prerequisites
3. Set risk level and click **Build SOP**
4. Download the ITIL-aligned SOP document

### 🔧 Troubleshooting Guide
1. Describe the issue title and symptoms
2. Select the technology stack
3. List what's already been tried
4. Enable decision tree option
5. Generate and download the guide

### 🔮 KB Gap Predictor
1. Enter your team's incident volume and top categories
2. Describe recurring issues
3. Click **Predict KB Gaps**
4. Get a prioritized list of KB articles to create with article stubs

---

## 🏗️ Architecture

```
kb_predictor/
├── app.py           # Streamlit UI (all tabs, styling, session state)
├── kb_engine.py     # LangChain + Ollama backend (prompts, chains, parsing)
├── requirements.txt # Python dependencies
└── README.md        # This file
```

**Flow:**
```
User Input → Streamlit UI → KBEngine
                              ├── LangChain PromptTemplate
                              ├── OllamaLLM (local LLMA)
                              └── Response Parsing → Structured Output → UI Display
```

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|---------|
| `Ollama not reachable` | Run `ollama serve` or check if port 11434 is in use |
| `Model not found` | Run `ollama pull <model-name>` |
| `Slow responses` | Use a smaller model like `llama3.2` or reduce `max_tokens` |
| `LangChain import error` | Run `pip install langchain-ollama langchain-community` |
| `Empty responses` | Increase `max_tokens`, lower `temperature` |

---

## 📦 Dependencies

- **Streamlit** - Web UI framework
- **LangChain** - LLM orchestration and prompt management  
- **langchain-ollama / langchain-community** - Ollama integration
- **Ollama** - Local LLM runtime (LLMA engine)
- **requests** - HTTP client for Ollama API

---

## 🤝 Extending the App

To add new generation types:
1. Add a new method in `KBEngine` class in `kb_engine.py`
2. Add a new tab in `app.py`
3. Follow the existing prompt template pattern

---

*Built with ❤️ using Streamlit + LangChain + Ollama*
