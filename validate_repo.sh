#!/bin/bash

# O-RAN × Nephio RAG Repository Validation Script
# Tests all README claims in Ubuntu 22.04 environment

set -e
set -x

echo "=== VALIDATION LOG START $(date) ==="
echo "Operating System: $(cat /etc/os-release | grep PRETTY_NAME)"
echo "Python Version: $(python3 --version)"
echo "Current Directory: $(pwd)"
echo "Files Present: $(ls -la | wc -l) files"

echo ""
echo "=== PHASE 1: DEPENDENCY INSTALLATION ==="

# Check if .env.example exists (README claim)
echo "Testing: .env.example file exists"
if [ -f ".env.example" ]; then
    echo "✅ PASS: .env.example found"
else
    echo "❌ FAIL: .env.example missing (README claims to copy this)"
fi

# Test Python virtual environment creation (README step 1)
echo ""
echo "Testing: Python virtual environment creation"
python3 -m venv test_venv || echo "❌ FAIL: venv creation failed"
if [ -d "test_venv" ]; then
    echo "✅ PASS: Virtual environment created"
    source test_venv/bin/activate
    echo "Python in venv: $(which python3)"
else
    echo "❌ FAIL: Virtual environment not created"
fi

# Test requirements.txt installation (README step 2)
echo ""
echo "Testing: pip install -r requirements.txt"
if pip3 install -r requirements.txt; then
    echo "✅ PASS: Requirements installed successfully"
else
    echo "❌ FAIL: Requirements installation failed"
    echo "Exit code: $?"
fi

echo ""
echo "=== PHASE 2: CORE FUNCTIONALITY TESTS ==="

# Test import capabilities (README Python examples)
echo "Testing: Python imports from src module"
python3 -c "
try:
    from src import create_rag_system
    print('✅ PASS: create_rag_system import successful')
except ImportError as e:
    print(f'❌ FAIL: create_rag_system import failed: {e}')

try:
    from src import quick_query
    print('✅ PASS: quick_query import successful')
except ImportError as e:
    print(f'❌ FAIL: quick_query import failed: {e}')

try:
    import src.config
    print('✅ PASS: config module import successful')
except ImportError as e:
    print(f'❌ FAIL: config module import failed: {e}')
"

# Test vector database creation (README step 2)
echo ""
echo "Testing: Vector database creation"
python3 -c "
try:
    from src import create_rag_system
    rag = create_rag_system()
    # Note: This may fail without proper API key
    print('✅ PASS: RAG system creation successful')
except Exception as e:
    print(f'❌ FAIL: RAG system creation failed: {e}')
" || echo "Expected failure without API configuration"

echo ""
echo "=== PHASE 3: DOCKER DEPLOYMENT TESTS ==="

# Test Docker Compose files exist (README claims)
echo "Testing: Docker Compose files presence"
for file in docker-compose.dev.yml docker-compose.prod.yml docker-compose.monitoring.yml; do
    if [ -f "$file" ]; then
        echo "✅ PASS: $file exists"
        # Test if compose file is valid
        if docker-compose -f "$file" config > /dev/null 2>&1; then
            echo "✅ PASS: $file is valid YAML"
        else
            echo "❌ FAIL: $file has invalid YAML syntax"
        fi
    else
        echo "❌ FAIL: $file missing"
    fi
done

# Test Dockerfile exists
echo ""
echo "Testing: Dockerfile presence and validity"
if [ -f "Dockerfile" ]; then
    echo "✅ PASS: Dockerfile exists"
    if docker build --dry-run . > /dev/null 2>&1; then
        echo "✅ PASS: Dockerfile syntax valid"
    else
        echo "❌ FAIL: Dockerfile has syntax errors"
    fi
else
    echo "❌ FAIL: Dockerfile missing"
fi

echo ""
echo "=== PHASE 4: DOCUMENTATION TESTS ==="

# Test referenced documentation files exist
echo "Testing: Referenced documentation files"
for doc in "docs/DOCKER_DEPLOYMENT.md"; do
    if [ -f "$doc" ]; then
        echo "✅ PASS: $doc exists"
    else
        echo "❌ FAIL: $doc missing (referenced in README)"
    fi
done

echo ""
echo "=== PHASE 5: TEST SUITE EXECUTION ==="

# Test pytest execution (if available)
echo "Testing: Test suite execution"
if command -v pytest > /dev/null; then
    if pytest --version > /dev/null 2>&1; then
        echo "✅ PASS: pytest available"
        if pytest tests/ -v --tb=short; then
            echo "✅ PASS: Test suite executed successfully"
        else
            echo "❌ FAIL: Tests failed or had errors"
        fi
    else
        echo "❌ FAIL: pytest not working properly"
    fi
else
    echo "⚠️  SKIP: pytest not installed"
fi

echo ""
echo "=== VALIDATION SUMMARY ==="
echo "Validation completed at $(date)"
echo "Check output above for detailed PASS/FAIL results"
echo "=== VALIDATION LOG END ==="