"""
Setup configuration for O-RAN × Nephio RAG System
"""
from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return "O-RAN × Nephio RAG System - Intelligent Retrieval-Augmented Generation"

# Read requirements
def read_requirements(filename):
    try:
        with open(filename, "r", encoding="utf-8") as fh:
            return [line.strip() for line in fh 
                   if line.strip() and not line.startswith("#") and not line.startswith("-r")]
    except FileNotFoundError:
        return []

# Version
__version__ = "1.0.0"

setup(
    name="oran-nephio-rag",
    version=__version__,
    author="Development Team",
    author_email="dev-team@company.com",
    description="O-RAN × Nephio RAG System - Intelligent Retrieval-Augmented Generation",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/company/oran-nephio-rag",
    packages=find_packages(include=["src", "src.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: System :: Networking",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10", 
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=read_requirements("requirements.txt"),
    extras_require={
        "dev": read_requirements("requirements-dev.txt"),
        "async": [
            "aiohttp>=3.8.0,<4.0.0",
            "asyncio-mqtt>=0.16.0,<1.0.0"
        ],
        "monitoring": [
            "prometheus-client>=0.17.0,<1.0.0",
            "grafana-api>=1.0.3,<2.0.0"
        ]
    },
    entry_points={
        "console_scripts": [
            "oran-rag=main:main",
            "oran-rag-sync=scripts.auto_sync:main",
            "oran-rag-test=scripts.test_system:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml", "*.json"],
        "docker": ["**/*"],
        "examples": ["*.py"],
        "docs": ["**/*"],
    },
    zip_safe=False,
    keywords=[
        "oran", "nephio", "rag", "ai", "langchain", "anthropic",
        "vector-database", "document-retrieval", "nlp", "5g", "telecom"
    ],
    project_urls={
        "Bug Reports": "https://github.com/company/oran-nephio-rag/issues",
        "Source": "https://github.com/company/oran-nephio-rag",
        "Documentation": "https://oran-nephio-rag.readthedocs.io/",
    },
)