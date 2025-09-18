# O-RAN × Nephio RAG System Test Suite

Comprehensive test suite for the O-RAN × Nephio RAG (Retrieval-Augmented Generation) system, following TDD principles and providing extensive coverage for all system components.

## 📋 Test Categories

### 1. Unit Tests (`test_core_rag_components.py`)
- **VectorDatabaseManager**: Database initialization, building, loading, searching
- **SklearnTfidfEmbeddings**: TF-IDF fallback embeddings implementation
- **QueryProcessor**: Query processing, Puter.js integration, fallback mechanisms
- **ORANNephioRAG**: Main system class, initialization, status management

### 2. Integration Tests (`test_integration_pipeline.py`)
- **Document Processing Pipeline**: End-to-end document loading and processing
- **Vector Database Creation**: Complete vector database building with real documents
- **Query Processing Flow**: Full query processing with realistic scenarios
- **Performance Integration**: Large-scale document processing performance

### 3. API Endpoint Tests (`test_api_endpoints.py`)
- **FastAPI Endpoints**: Health, status, query, batch query endpoints
- **Query Types**: Architecture, scaling, O-RAN, deployment, complex queries
- **Error Handling**: Validation errors, system failures, malformed requests
- **Performance**: Concurrent requests, batch processing, large queries

### 4. Performance Tests (`test_performance_benchmarks.py`)
- **Query Performance**: Response times, throughput, concurrent processing
- **Vector Database Performance**: Building, searching, large document sets
- **Memory Performance**: Usage monitoring, leak detection, cleanup
- **Throughput Benchmarks**: Sequential, parallel, mixed workload testing

### 5. Accuracy Tests (`test_response_accuracy.py`)
- **Response Relevance**: Keyword coverage, concept matching, query alignment
- **Response Quality**: Coherence, completeness, factual accuracy
- **Source Quality**: Authority, credibility, content quality assessment
- **Comprehensive Metrics**: Multi-dimensional accuracy evaluation

### 6. Mock Data & Scenarios (`test_mock_data_scenarios.py`)
- **Nephio Clusters**: Multi-tier cluster configurations (core, edge, far-edge)
- **O-RAN Components**: O-CU, O-DU, O-RU with realistic configurations
- **Scaling Scenarios**: Horizontal, vertical, geographic, hybrid scaling
- **Realistic Documents**: Architecture, integration, scaling procedure documents

### 7. Test Fixtures & Utilities (`test_fixtures_utilities.py`)
- **DocumentFactory**: Create test documents with realistic content
- **MockRAGSystemBuilder**: Build mock systems with specific behaviors
- **TestEnvironmentManager**: Manage test environments and cleanup
- **Performance Utilities**: Timing, memory monitoring, validation helpers

### 8. Edge Cases & Error Handling (`test_edge_cases_errors.py`)
- **Edge Cases**: Empty queries, very long/short queries, special characters
- **Error Conditions**: Timeouts, memory errors, connection failures
- **Resource Exhaustion**: Memory limits, rate limiting, complexity limits
- **Recovery Mechanisms**: Automatic recovery, failure handling, resilience

### 9. Browser Automation Tests (`test_browser_automation.py`)
- **Puter.js Integration**: Browser initialization, availability checks
- **Query Execution**: Browser-based query processing through Puter.js
- **Error Scenarios**: Browser failures, session management, timeouts
- **Performance**: Browser automation timing, concurrent sessions

### 10. Comprehensive Reporting (`test_comprehensive_reporting.py`)
- **Test Metrics**: Coverage, performance, quality scoring
- **Report Generation**: HTML, JSON, JUnit XML formats
- **Performance Profiling**: Execution time analysis, bottleneck identification
- **Quality Analysis**: Multi-dimensional quality assessment

## 🚀 Running Tests

### Prerequisites
```bash
pip install -r requirements.txt
pip install pytest pytest-cov pytest-html pytest-timeout pytest-mock
```

### Run All Tests
```bash
# Run complete test suite
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src --cov-report=html
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest -m unit

# Integration tests
pytest -m integration

# Performance tests (may take longer)
pytest -m performance

# Quick tests (exclude slow tests)
pytest -m "not slow"

# Browser automation tests
pytest -m browser

# Accuracy tests
pytest -m accuracy
```

### Run Specific Test Files
```bash
# Core component tests
pytest tests/test_core_rag_components.py

# API endpoint tests
pytest tests/test_api_endpoints.py

# Performance benchmarks
pytest tests/test_performance_benchmarks.py
```

## 📊 Test Reports

Test execution generates comprehensive reports in the `test_reports/` directory:

- **HTML Report**: `test_reports/pytest_report.html` - Interactive test results
- **Coverage Report**: `test_reports/coverage_html/index.html` - Code coverage analysis
- **JUnit XML**: `test_reports/junit_report.xml` - CI/CD integration
- **Performance Analysis**: `test_reports/performance_analysis.json` - Performance metrics
- **Quality Analysis**: `test_reports/quality_analysis.json` - Test quality assessment

## 🏗️ Test Architecture

### Test Design Principles

1. **Test-Driven Development (TDD)**
   - Tests written before or alongside implementation
   - Red-Green-Refactor cycle
   - Comprehensive test coverage

2. **Isolation and Mocking**
   - All external dependencies mocked
   - Tests run independently
   - No network calls or file system dependencies

3. **Realistic Test Data**
   - Nephio and O-RAN specific scenarios
   - Realistic document content
   - Production-like configurations

4. **Performance Awareness**
   - Performance tests for all critical paths
   - Memory usage monitoring
   - Throughput and latency benchmarks

### Mock Strategy

- **Puter.js Integration**: Mocked browser automation and API calls
- **Vector Database**: Mocked ChromaDB operations
- **Document Loading**: Mocked HTTP requests with realistic responses
- **LLM Responses**: Configurable mock responses for different scenarios

### Fixtures and Utilities

The test suite provides extensive fixtures and utilities:

- **DocumentFactory**: Generate realistic test documents
- **MockRAGSystemBuilder**: Build mock systems with specific behaviors
- **TestEnvironmentManager**: Manage test environments and cleanup
- **PerformanceTimer**: Measure execution times
- **ResponseValidator**: Validate response structures
- **TestAssertions**: Custom assertions for RAG systems

## 🔧 Configuration

### Environment Variables
```bash
# Test environment
export API_MODE=mock
export ANTHROPIC_API_KEY=test-key

# Test database paths
export VECTOR_DB_PATH=./test_vectordb
export EMBEDDINGS_CACHE_PATH=./test_embeddings

# Performance settings
export CHUNK_SIZE=256
export RETRIEVER_K=3
```

### pytest.ini Configuration
The `pytest.ini` file provides comprehensive test configuration:
- Test discovery patterns
- Coverage requirements (minimum 80%)
- Report generation settings
- Marker definitions
- Logging configuration

## 📈 Performance Benchmarks

### Target Performance Metrics

- **Query Response Time**: < 2 seconds average
- **Vector Database Build**: < 30 seconds for 100 documents
- **Memory Usage**: < 500MB increase during testing
- **Throughput**: > 5 queries per second
- **Test Coverage**: > 80% code coverage

### Performance Test Categories

1. **Response Time Tests**: Individual query performance
2. **Throughput Tests**: Concurrent query handling
3. **Memory Tests**: Memory usage and leak detection
4. **Stress Tests**: System behavior under load

## 🎯 Quality Metrics

### Test Quality Scoring

Tests are evaluated on multiple dimensions:
- **Pass Rate** (40%): Percentage of passing tests
- **Coverage** (30%): Code coverage percentage
- **Performance** (30%): Execution time efficiency

### Quality Thresholds

- **Excellent**: Score ≥ 80/100
- **Good**: Score ≥ 60/100
- **Needs Improvement**: Score < 60/100

## 🔄 Continuous Integration

### CI/CD Integration

The test suite is designed for CI/CD integration:
- JUnit XML reports for build systems
- Coverage reports for code quality gates
- Performance regression detection
- Automated test execution on pull requests

### GitHub Actions Example
```yaml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-html
      - name: Run tests
        run: pytest
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

## 🛠️ Development Guidelines

### Adding New Tests

1. **Choose Appropriate Category**: Unit, integration, performance, etc.
2. **Use Existing Fixtures**: Leverage DocumentFactory, mock builders
3. **Follow Naming Conventions**: `test_*` functions, descriptive names
4. **Add Markers**: Use pytest markers for categorization
5. **Document Test Purpose**: Clear docstrings and comments

### Test Data Management

- Use `DocumentFactory` for consistent test documents
- Leverage mock data scenarios for realistic testing
- Avoid hardcoded test data in favor of factories
- Ensure test data represents real Nephio/O-RAN scenarios

### Performance Testing

- Always include performance assertions
- Use `PerformanceTimer` for consistent timing
- Monitor memory usage in long-running tests
- Set realistic performance thresholds

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Coverage](https://pytest-cov.readthedocs.io/)
- [Nephio Documentation](https://docs.nephio.org/)
- [O-RAN Alliance](https://www.o-ran.org/)

## 🤝 Contributing

When contributing to the test suite:

1. **Run Full Test Suite**: Ensure all tests pass
2. **Add Tests for New Features**: Follow TDD principles
3. **Update Documentation**: Keep README and docstrings current
4. **Check Coverage**: Maintain >80% coverage requirement
5. **Performance Impact**: Consider performance implications

For questions or contributions, please follow the project's contribution guidelines.