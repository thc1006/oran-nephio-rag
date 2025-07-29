# 🏗️ O-RAN × Nephio RAG: Intelligent Retrieval-Augmented Generation System

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-0.2.16-green.svg)](https://langchain.com/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![Claude](https://img.shields.io/badge/Claude-3.0-purple.svg)](https://www.anthropic.com/)

> **Professional O-RAN and Nephio Integration Knowledge Retrieval System**  
> Built on official documentation to provide accurate and reliable technical Q&A services

## 🌟 Core Features

### 🎯 **Official Documentation Priority Strategy**
- 📚 **Authoritative Sources**: Focuses exclusively on O-RAN SC and Nephio official documentation
- 🔄 **Real-time Synchronization**: Automatically updates with the latest released content
- ✅ **Accuracy Guarantee**: Avoids outdated or inaccurate online information

### 🚀 **Advanced Technical Architecture**
- 🤖 **Claude 3.0 AI**: Latest Anthropic large language model
- 🔍 **Vector Retrieval**: ChromaDB + Sentence-Transformers semantic search
- 📊 **RAG Architecture**: Retrieval-Augmented Generation ensuring answer accuracy
- 🌐 **Multi-language Support**: Comprehensive English interface and responses

### 💼 **Professional Application Scenarios**
- 🏗️ **NF Scale-out Implementation**: Detailed O-RAN DU/CU scale-out on Nephio
- 🔧 **Integration Architecture**: O2IMS interfaces, FOCOM, SMO collaboration mechanisms
- 📋 **Deployment Guides**: Production environment best practices

## 📁 Project Structure

```
oran-nephio-rag/
├── 📄 README.md                    # This file
├── 📋 requirements.txt              # Python dependencies
├── 🔐 .env.example                 # Environment variables template
├── 🚫 .gitignore                   # Git ignore rules
├── 🚀 main.py                      # Main program entry point
├── 📁 src/                         # Core source code
│   ├── 🔗 __init__.py
│   ├── 🧠 oran_nephio_rag.py       # RAG system core
│   ├── 📚 document_loader.py        # Document loader
│   └── ⚙️ config.py                # Configuration management
├── 📁 scripts/                     # Utility scripts
│   ├── 🔄 auto_sync.py             # Automatic synchronization service
│   └── 🧪 test_system.py           # System testing
├── 📁 examples/                    # Usage examples
│   ├── 🔗 __init__.py
│   └── 💡 example_usage.py         # Feature demonstrations
├── 📁 tests/                       # Unit tests
│   ├── 🔗 __init__.py
│   ├── 🧪 test_config.py
│   ├── 🧪 test_document_loader.py
│   └── 🧪 test_rag_system.py
├── 📁 docs/                        # Detailed documentation
│   └── 📖 SETUP.md                 # Installation setup guide
├── 📁 logs/                        # System logs (auto-created)
├── 📁 oran_nephio_vectordb/        # Vector database (auto-created)
└── 📁 embeddings_cache/            # Embedding model cache (auto-created)
```

## 🚀 Quick Start

### 📋 System Requirements

- **Python**: 3.10 or higher
- **Operating System**: Windows 10/11, macOS, Linux
- **Memory**: Recommended 8GB or more
- **Disk Space**: At least 2GB available space
- **API Key**: Anthropic Claude API Key

### ⚡ 3-Minute Installation

```bash
# 1️⃣ Clone the project
git clone https://github.com/thc1006/oran-nephio-rag.git
cd oran-nephio-rag
```

```bash
# 2️⃣ Create Python virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux  
source .venv/bin/activate
```

```bash
# 3️⃣ Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

```bash
# 4️⃣ Configure environment variables
cp .env.example .env
# Edit .env file and add your ANTHROPIC_API_KEY
```

```bash
# 5️⃣ Run system test
python scripts/test_system.py
```

```bash
# 6️⃣ Start the system
python main.py
```

## 💡 Usage

### 🎯 **Interactive Query**

After starting the system, you can ask questions about O-RAN and Nephio integration:

```
🤖 O-RAN × Nephio RAG System
Enter your question (type 'quit' or 'exit' to end): 

❓ How to implement O-RAN DU scale-out on Nephio?

💡 Answer:
Implementing O-RAN DU (Distributed Unit) scale-out on the Nephio platform requires considering the following key steps...

📚 Reference Sources (3):
  1. [NEPHIO] Nephio O-RAN Integration Architecture
  2. [ORAN_SC] O-RAN DU Scaling Best Practices  
  3. [NEPHIO] Free5GC NF Deployment Guide

⚡ Query Time: 2.3 seconds
```

### 🔧 **Programmatic Usage**

```python
from src.oran_nephio_rag import ORANNephioRAG, quick_query

# Quick query
answer = quick_query("What is the O2IMS interface?")

# Full functionality usage
rag = ORANNephioRAG()
rag.load_documents()  # Load documents on first use
result = rag.query("What is the role of FOCOM in O-RAN architecture?")
```

### 📊 **Common Query Examples**

| Question Category | Example Question |
|---------|---------|
| **Architecture Design** | "What is the integration architecture of O-RAN and Nephio?" |
| **NF Scaling** | "How to implement horizontal scaling of O-RAN CU?" |
| **Interface Protocols** | "What are the main functions and design principles of O2IMS interface?" |
| **Deployment Practices** | "Best practices for deploying O-RAN DU in production environments?" |
| **Troubleshooting** | "Common causes and solutions for O-RAN NF scaling failures?" |

## 🔧 Advanced Configuration

### ⚙️ **Environment Variables Explained**

```env
# 🔑 Required Configuration
ANTHROPIC_API_KEY=sk-ant-api03-your-api-key

# 🤖 Claude Model Settings
CLAUDE_MODEL=claude-3-sonnet-20240229    # Model version
CLAUDE_MAX_TOKENS=4000                    # Maximum response length
CLAUDE_TEMPERATURE=0.1                    # Creativity level (0-1)

# 📊 Vector Database Settings
VECTOR_DB_PATH=./oran_nephio_vectordb     # Database path
COLLECTION_NAME=oran_nephio_official      # Collection name
CHUNK_SIZE=1000                           # Text chunk size
CHUNK_OVERLAP=200                         # Overlap characters

# 🔄 Auto-sync Settings
AUTO_SYNC_ENABLED=true                    # Enable auto-sync
SYNC_INTERVAL_HOURS=24                    # Sync interval (hours)

# 📝 Logging Settings
LOG_LEVEL=INFO                            # Log level
LOG_FILE=logs/oran_nephio_rag.log         # Log file path
```

### 🔄 **Auto-sync Service**

```bash
# Start auto-sync background service
python scripts/auto_sync.py --daemon

# Manually execute sync once
python scripts/auto_sync.py --once

# Check sync status
python scripts/auto_sync.py --status
```

## 📚 Supported Official Documentation Sources

### 🏛️ **Nephio Official Documentation**
- 📖 [Core Architecture Documentation](https://docs.nephio.org/docs/architecture/)
- 🔧 [O-RAN Integration Guide](https://docs.nephio.org/docs/network-architecture/o-ran-integration/)
- 💻 [User Guides](https://docs.nephio.org/docs/guides/user-guides/)
- 📋 [Installation & Deployment](https://docs.nephio.org/docs/installation/)

### 🌐 **O-RAN SC Official Resources**
- 📚 [Technical Specification Documents](https://oransc.org/specifications/)
- 🏗️ [Architecture Reference](https://wiki.o-ran-sc.org/)
- 🔧 [Implementation Guides](https://docs.o-ran-sc.org/)
- 📊 [Release Notes](https://wiki.o-ran-sc.org/display/REL)

## 🧪 Testing & Quality Assurance

### ✅ **Automated Testing**

```bash
# Run complete test suite
pytest tests/ -v

# Run specific test module
pytest tests/test_rag_system.py -v

# Run tests and generate coverage report
pytest tests/ --cov=src --cov-report=html
```

### 📊 **System Health Check**

```bash
# Complete system test
python scripts/test_system.py

# Quick health check
python -c "from src.oran_nephio_rag import quick_query; print(quick_query('test'))"
```

## 🛠️ Troubleshooting

### ❗ **Common Issues**

<details>
<summary>📦 <strong>ChromaDB Installation Failure</strong></summary>

**Issue**: `pip install chromadb` fails  
**Solution**:
```bash
# Windows: Ensure Visual C++ Build Tools are installed
# Then try:
pip install --no-cache-dir chromadb==0.5.3

# Or use conda:
conda install -c conda-forge chromadb
```
</details>

<details>
<summary>🔑 <strong>API Key Issues</strong></summary>

**Issue**: API key invalid or quota insufficient  
**Solution**:
1. Check `ANTHROPIC_API_KEY` in `.env` file
2. Ensure key format: `sk-ant-api03-...`
3. Login to [Anthropic Console](https://console.anthropic.com/) to check quota
</details>

<details>
<summary>🚀 <strong>Memory Issues</strong></summary>

**Issue**: System memory usage too high  
**Solution**:
```env
# Adjust parameters in .env
CHUNK_SIZE=512          # Reduce text chunk size
CLAUDE_MAX_TOKENS=2000  # Reduce response length
```
</details>

### 📞 **Technical Support**

If you encounter unresolvable issues, please:

1. 🐛 **Submit Issue**: Create detailed problem report on GitHub
2. 📧 **Contact Developer**: thc1006@example.com
3. 💬 **Community Discussion**: Join Nephio community Slack channels

## 🤝 Contributing Guidelines

Welcome to contribute to the project! Please follow these steps:

```bash
# 1️⃣ Fork the project and clone
git clone https://github.com/your-username/oran-nephio-rag.git

# 2️⃣ Create feature branch
git checkout -b feature/amazing-feature

# 3️⃣ Make changes and commit
git commit -m "Add amazing feature"

# 4️⃣ Push to branch
git push origin feature/amazing-feature

# 5️⃣ Submit Pull Request
```

### 📝 **Contribution Types**

- 🐛 Bug fixes
- ✨ New feature development  
- 📚 Documentation improvements
- 🧪 Test enhancements
- 🎨 Code quality optimizations

## 📜 License

This project is licensed under the [Apache 2.0 License](LICENSE). You are free to use, modify, and distribute, but must retain the original license notice.

## 🌟 Acknowledgments

Special thanks to the following open source projects and communities:

- 🦜 **LangChain**: Powerful LLM application development framework
- 🤖 **Anthropic**: Providing Claude AI models
- 🔍 **ChromaDB**: Efficient vector database
- 🏗️ **Nephio Project**: Cloud-native network function orchestration
- 🌐 **O-RAN Alliance**: Open RAN architecture standards

---

<div align="center">

**🚀 Ready to explore the infinite possibilities of O-RAN × Nephio?**

[Get Started](#-quick-start) | [View Examples](examples/) | [Read Docs](docs/) | [Submit Issues](../../issues)

</div>