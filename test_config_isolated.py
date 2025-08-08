#!/usr/bin/env python3
"""
Isolated test configuration for O-RAN × Nephio RAG system
Runs tests without external dependencies
"""
import os
import sys
import subprocess
from typing import List, Dict, Any


def get_safe_tests() -> List[str]:
    """Get list of test files that can run without heavy dependencies"""
    safe_tests = [
        "tests/test_config.py",
        "tests/test_document_loader.py", 
        "tests/test_utils.py",
        "test_basic_imports.py"
    ]
    
    # Check which test files actually exist
    existing_tests = []
    for test_file in safe_tests:
        if os.path.exists(test_file):
            existing_tests.append(test_file)
        else:
            print(f"[WARN] Test file not found, skipping: {test_file}")
    
    return existing_tests


def run_isolated_tests(verbose: bool = True) -> Dict[str, Any]:
    """Run isolated tests that don't require external dependencies"""
    safe_tests = get_safe_tests()
    
    if not safe_tests:
        return {
            "success": False,
            "error": "No safe test files found",
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0
        }
    
    # Prepare pytest command
    cmd = [
        sys.executable, "-m", "pytest",
        *safe_tests,
        "--tb=short",
        "--no-cov",  # Disable coverage to avoid issues
        "-x",  # Stop on first failure for faster feedback
    ]
    
    if verbose:
        cmd.append("-v")
    
    # Add markers to skip problematic tests
    cmd.extend([
        "-m", "not requires_heavy_deps and not requires_api_key and not requires_network"
    ])
    
    print("[INFO] Running isolated test suite...")
    print(f"   Tests: {', '.join(safe_tests)}")
    print(f"   Command: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        # Parse results
        success = result.returncode == 0
        output_lines = result.stdout.split('\n')
        
        # Extract test counts from pytest output
        summary_line = [line for line in output_lines if "passed" in line and ("failed" in line or "error" in line or line.endswith("passed"))]
        
        tests_passed = 0
        tests_failed = 0
        tests_run = 0
        
        if summary_line:
            line = summary_line[-1]
            if "passed" in line:
                # Parse numbers from summary line
                import re
                passed_match = re.search(r'(\d+) passed', line)
                failed_match = re.search(r'(\d+) failed', line)
                error_match = re.search(r'(\d+) error', line)
                
                tests_passed = int(passed_match.group(1)) if passed_match else 0
                tests_failed = int(failed_match.group(1)) if failed_match else 0
                tests_failed += int(error_match.group(1)) if error_match else 0
                tests_run = tests_passed + tests_failed
        
        return {
            "success": success,
            "tests_run": tests_run,
            "tests_passed": tests_passed,
            "tests_failed": tests_failed,
            "output": result.stdout,
            "errors": result.stderr,
            "return_code": result.returncode
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Tests timed out after 5 minutes",
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to run tests: {str(e)}",
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0
        }


def create_test_environment_file():
    """Create a test environment configuration"""
    test_env_content = """# Test Environment Configuration for O-RAN × Nephio RAG System
# This file contains safe defaults for testing without external dependencies

# API Configuration (Mock Mode)
API_MODE=mock
PUTER_MODEL=claude-sonnet-4

# Vector Database Configuration  
VECTOR_DB_PATH=./test_vectordb
EMBEDDINGS_CACHE_PATH=./test_embeddings
COLLECTION_NAME=test_collection

# Model Configuration
MAX_TOKENS=1000
TEMPERATURE=0.1

# Document Loading Configuration
MAX_RETRIES=2
REQUEST_TIMEOUT=10
CHUNK_SIZE=512
CHUNK_OVERLAP=100

# Validation Configuration (Relaxed for Testing)
MIN_CONTENT_LENGTH=100
MIN_EXTRACTED_CONTENT_LENGTH=50
MIN_LINE_LENGTH=3

# Logging Configuration
LOG_LEVEL=DEBUG
LOG_FILE=./test_logs/test.log

# Browser Configuration (for Testing)
BROWSER_HEADLESS=true
BROWSER_TIMEOUT=30
BROWSER_WAIT_TIME=3

# Sync Configuration
AUTO_SYNC_ENABLED=false
SYNC_INTERVAL_HOURS=24

# Retrieval Configuration
RETRIEVER_K=3
RETRIEVER_FETCH_K=6
RETRIEVER_LAMBDA_MULT=0.7

# Security Configuration
VERIFY_SSL=false
SSL_TIMEOUT=10
"""
    
    with open('.env.test', 'w', encoding='utf-8') as f:
        f.write(test_env_content)
    
    print("[INFO] Created .env.test file with safe test configuration")


def main():
    """Main test runner"""
    print(">> O-RAN x Nephio RAG System - Isolated Test Suite")
    print("=" * 60)
    
    # Create test environment file
    create_test_environment_file()
    
    # Set test environment
    os.environ.update({
        "TESTING": "true",
        "API_MODE": "mock",
        "VECTOR_DB_PATH": "./test_vectordb",
        "MIN_CONTENT_LENGTH": "100",
        "LOG_LEVEL": "DEBUG"
    })
    
    # Run tests
    results = run_isolated_tests(verbose=True)
    
    print("\n" + "=" * 60)
    print(">> TEST RESULTS SUMMARY")
    print("=" * 60)
    
    if results["success"]:
        print(f"[PASS] Status: PASSED")
        print(f"[INFO] Tests Run: {results['tests_run']}")
        print(f"[PASS] Tests Passed: {results['tests_passed']}")
        print(f"[FAIL] Tests Failed: {results['tests_failed']}")
        print(f"[INFO] Success Rate: {(results['tests_passed']/results['tests_run']*100):.1f}%" if results['tests_run'] > 0 else "N/A")
    else:
        print(f"[FAIL] Status: FAILED")
        if "error" in results:
            print(f"[ERROR] Error: {results['error']}")
        else:
            print(f"[INFO] Tests Run: {results['tests_run']}")
            print(f"[PASS] Tests Passed: {results['tests_passed']}")
            print(f"[FAIL] Tests Failed: {results['tests_failed']}")
    
    print("\n" + "=" * 60)
    print(">> RECOMMENDATIONS")
    print("=" * 60)
    
    if results["success"]:
        print("[PASS] All isolated tests are passing!")
        print("[INFO] Core functionality (config, document loading, utils) is working")
        print("[INFO] To run all tests: python -m pytest tests/")
        print("[INFO] Ready for development and deployment")
    else:
        print("[WARN] Some tests are failing - check the output above")
        print("[INFO] Run individual test files to debug specific issues")
        print("[INFO] Fix failing tests before proceeding with development")
    
    print("\n[INFO] To run specific test categories:")
    print("   • Unit tests only: pytest -m unit")
    print("   • Skip slow tests: pytest -m 'not slow'")
    print("   • Skip heavy dependencies: pytest -m 'not requires_heavy_deps'")
    
    return 0 if results["success"] else 1


if __name__ == "__main__":
    sys.exit(main())