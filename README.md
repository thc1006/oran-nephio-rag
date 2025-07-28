# O-RAN × Nephio RAG

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)


## 🎯 Key Features

- **Official Documentation Priority**: Retrieves information exclusively from O-RAN SC and Nephio official documentation
- **Accuracy Guarantee**: Avoids outdated or inaccurate web information
- **Professional Focus**: Concentrates on NF scaling implementation details
- **Real-time Updates**: Automatically syncs with the latest official documentation
- **Chinese Support**: Complete Traditional Chinese interface and responses

## File Structure
```
oran-nephio-rag/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── main.py
├── src/
│   ├── __init__.py
│   ├── oran_nephio_rag.py
│   ├── document_loader.py
│   └── config.py
├── scripts/
│   ├── auto_sync.py
│   └── test_system.py
├── examples/
│   └── example_usage.py
├── docs/
│   └── SETUP.md
└── logs/ (created automatically at runtime)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Microsoft Visual C++ Build Tools (Windows)
- Anthropic API Key

### Installation Steps

```bash
# 1. Clone the repository
git clone https://github.com/your-username/oran-nephio-rag.git
cd oran-nephio-rag
```

```bash
# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS
```

```bash
# 3. Install dependencies
pip install -r requirements.txt
```

```bash
# 4. Configure environment variables
cp .env.example .env
# Edit the .env file and add your ANTHROPIC_API_KEY
```

```bash
# 5. Run the system
python main.py
```

## 📖 Usage

After starting the system, you can ask questions about O-RAN and Nephio integration:

- "How to implement O-RAN DU scale-out on Nephio?"
- "What role does the O2IMS interface play in NF scaling?"
- "How do FOCOM and SMO collaborate for automatic scaling?"

## 🛠️ Supported Documentation Sources

- [O-RAN SC Confluence](https://lf-o-ran-sc.atlassian.net/wiki/spaces/ORAN/overview)
- [Nephio Documentation](https://docs.nephio.org/)
- O-RAN SC official blogs and technical specifications

## 📝 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Issues and Pull Requests are welcome! Please refer to [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.
