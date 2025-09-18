"""
Comprehensive test reporting and metrics
Testing: Test coverage, performance metrics, quality reports, CI/CD integration
"""

import os
import pytest
import json
import time
import subprocess
import sys
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import xml.etree.ElementTree as ET


@dataclass
class TestMetrics:
    """Test execution metrics"""
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    skipped_tests: int = 0
    error_tests: int = 0
    execution_time: float = 0.0
    coverage_percentage: float = 0.0
    performance_score: float = 0.0
    quality_score: float = 0.0


@dataclass
class TestCategory:
    """Test category metrics"""
    name: str
    tests: List[str] = field(default_factory=list)
    metrics: TestMetrics = field(default_factory=TestMetrics)
    description: str = ""


class TestReportGenerator:
    """Generate comprehensive test reports"""

    def __init__(self, output_dir: str = "test_reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.start_time = datetime.now()
        self.test_categories = {}
        self.overall_metrics = TestMetrics()

    def add_test_category(self, name: str, description: str = "") -> TestCategory:
        """Add a test category for tracking"""
        category = TestCategory(name=name, description=description)
        self.test_categories[name] = category
        return category

    def record_test_result(self, category: str, test_name: str, result: str, duration: float = 0.0):
        """Record individual test result"""
        if category not in self.test_categories:
            self.add_test_category(category)

        cat = self.test_categories[category]
        cat.tests.append(test_name)
        cat.metrics.total_tests += 1
        cat.metrics.execution_time += duration

        if result == "passed":
            cat.metrics.passed_tests += 1
        elif result == "failed":
            cat.metrics.failed_tests += 1
        elif result == "skipped":
            cat.metrics.skipped_tests += 1
        elif result == "error":
            cat.metrics.error_tests += 1

    def calculate_quality_scores(self):
        """Calculate quality scores for each category"""
        for category in self.test_categories.values():
            metrics = category.metrics
            if metrics.total_tests > 0:
                # Pass rate score (0-40 points)
                pass_rate = metrics.passed_tests / metrics.total_tests
                pass_score = pass_rate * 40

                # Coverage score (0-30 points)
                coverage_score = min(metrics.coverage_percentage / 100 * 30, 30)

                # Performance score (0-30 points)
                # Lower execution time per test is better
                avg_time_per_test = metrics.execution_time / metrics.total_tests
                if avg_time_per_test <= 0.1:
                    perf_score = 30
                elif avg_time_per_test <= 1.0:
                    perf_score = 25
                elif avg_time_per_test <= 5.0:
                    perf_score = 15
                else:
                    perf_score = 5

                metrics.quality_score = pass_score + coverage_score + perf_score

    def generate_html_report(self) -> str:
        """Generate HTML test report"""
        self.calculate_quality_scores()

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>O-RAN × Nephio RAG System Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .summary {{ margin: 20px 0; }}
                .category {{ margin: 20px 0; border: 1px solid #ddd; border-radius: 5px; }}
                .category-header {{ background-color: #e9e9e9; padding: 15px; font-weight: bold; }}
                .category-content {{ padding: 15px; }}
                .metrics {{ display: flex; gap: 20px; margin: 10px 0; }}
                .metric {{ text-align: center; padding: 10px; border: 1px solid #ccc; border-radius: 3px; }}
                .passed {{ background-color: #d4edda; }}
                .failed {{ background-color: #f8d7da; }}
                .skipped {{ background-color: #fff3cd; }}
                .coverage {{ background-color: #d1ecf1; }}
                .quality-high {{ color: #28a745; }}
                .quality-medium {{ color: #ffc107; }}
                .quality-low {{ color: #dc3545; }}
                table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .test-list {{ max-height: 200px; overflow-y: auto; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>O-RAN × Nephio RAG System Test Report</h1>
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Test Execution Duration: {(datetime.now() - self.start_time).total_seconds():.2f} seconds</p>
            </div>

            <div class="summary">
                <h2>Overall Summary</h2>
                {self._generate_overall_summary_html()}
            </div>

            <div class="categories">
                <h2>Test Categories</h2>
                {self._generate_categories_html()}
            </div>

            <div class="details">
                <h2>Detailed Results</h2>
                {self._generate_detailed_results_html()}
            </div>
        </body>
        </html>
        """

        report_path = self.output_dir / "test_report.html"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return str(report_path)

    def _generate_overall_summary_html(self) -> str:
        """Generate overall summary HTML"""
        total_tests = sum(cat.metrics.total_tests for cat in self.test_categories.values())
        total_passed = sum(cat.metrics.passed_tests for cat in self.test_categories.values())
        total_failed = sum(cat.metrics.failed_tests for cat in self.test_categories.values())
        total_skipped = sum(cat.metrics.skipped_tests for cat in self.test_categories.values())
        total_time = sum(cat.metrics.execution_time for cat in self.test_categories.values())

        pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0

        return f"""
        <div class="metrics">
            <div class="metric">
                <h3>Total Tests</h3>
                <div style="font-size: 24px;">{total_tests}</div>
            </div>
            <div class="metric passed">
                <h3>Passed</h3>
                <div style="font-size: 24px;">{total_passed}</div>
            </div>
            <div class="metric failed">
                <h3>Failed</h3>
                <div style="font-size: 24px;">{total_failed}</div>
            </div>
            <div class="metric skipped">
                <h3>Skipped</h3>
                <div style="font-size: 24px;">{total_skipped}</div>
            </div>
            <div class="metric">
                <h3>Pass Rate</h3>
                <div style="font-size: 24px;">{pass_rate:.1f}%</div>
            </div>
            <div class="metric">
                <h3>Total Time</h3>
                <div style="font-size: 24px;">{total_time:.2f}s</div>
            </div>
        </div>
        """

    def _generate_categories_html(self) -> str:
        """Generate test categories HTML"""
        html = ""
        for name, category in self.test_categories.items():
            metrics = category.metrics

            quality_class = "quality-high" if metrics.quality_score >= 80 else \
                           "quality-medium" if metrics.quality_score >= 60 else "quality-low"

            html += f"""
            <div class="category">
                <div class="category-header">
                    {name.title()} Tests - {category.description}
                    <span class="{quality_class}" style="float: right;">Quality Score: {metrics.quality_score:.1f}/100</span>
                </div>
                <div class="category-content">
                    <div class="metrics">
                        <div class="metric">
                            <strong>Total:</strong> {metrics.total_tests}
                        </div>
                        <div class="metric passed">
                            <strong>Passed:</strong> {metrics.passed_tests}
                        </div>
                        <div class="metric failed">
                            <strong>Failed:</strong> {metrics.failed_tests}
                        </div>
                        <div class="metric skipped">
                            <strong>Skipped:</strong> {metrics.skipped_tests}
                        </div>
                        <div class="metric">
                            <strong>Time:</strong> {metrics.execution_time:.2f}s
                        </div>
                        <div class="metric coverage">
                            <strong>Coverage:</strong> {metrics.coverage_percentage:.1f}%
                        </div>
                    </div>
                </div>
            </div>
            """

        return html

    def _generate_detailed_results_html(self) -> str:
        """Generate detailed results HTML"""
        html = ""
        for name, category in self.test_categories.items():
            html += f"""
            <h3>{name.title()} Tests</h3>
            <div class="test-list">
                <table>
                    <thead>
                        <tr>
                            <th>Test Name</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
            """

            for test in category.tests[:20]:  # Show first 20 tests
                html += f"""
                        <tr>
                            <td>{test}</td>
                            <td><span class="passed">PASSED</span></td>
                        </tr>
                """

            if len(category.tests) > 20:
                html += f"""
                        <tr>
                            <td colspan="2"><em>... and {len(category.tests) - 20} more tests</em></td>
                        </tr>
                """

            html += """
                    </tbody>
                </table>
            </div>
            """

        return html

    def generate_json_report(self) -> str:
        """Generate JSON test report"""
        self.calculate_quality_scores()

        report_data = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "execution_duration": (datetime.now() - self.start_time).total_seconds(),
                "report_version": "1.0"
            },
            "overall_summary": {
                "total_tests": sum(cat.metrics.total_tests for cat in self.test_categories.values()),
                "passed_tests": sum(cat.metrics.passed_tests for cat in self.test_categories.values()),
                "failed_tests": sum(cat.metrics.failed_tests for cat in self.test_categories.values()),
                "skipped_tests": sum(cat.metrics.skipped_tests for cat in self.test_categories.values()),
                "total_execution_time": sum(cat.metrics.execution_time for cat in self.test_categories.values())
            },
            "categories": {}
        }

        for name, category in self.test_categories.items():
            report_data["categories"][name] = {
                "description": category.description,
                "metrics": {
                    "total_tests": category.metrics.total_tests,
                    "passed_tests": category.metrics.passed_tests,
                    "failed_tests": category.metrics.failed_tests,
                    "skipped_tests": category.metrics.skipped_tests,
                    "execution_time": category.metrics.execution_time,
                    "coverage_percentage": category.metrics.coverage_percentage,
                    "quality_score": category.metrics.quality_score
                },
                "tests": category.tests
            }

        report_path = self.output_dir / "test_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)

        return str(report_path)

    def generate_junit_xml(self) -> str:
        """Generate JUnit XML report for CI/CD integration"""
        root = ET.Element("testsuites")
        root.set("name", "O-RAN Nephio RAG Tests")
        root.set("tests", str(sum(cat.metrics.total_tests for cat in self.test_categories.values())))
        root.set("failures", str(sum(cat.metrics.failed_tests for cat in self.test_categories.values())))
        root.set("errors", str(sum(cat.metrics.error_tests for cat in self.test_categories.values())))
        root.set("time", str(sum(cat.metrics.execution_time for cat in self.test_categories.values())))

        for name, category in self.test_categories.items():
            testsuite = ET.SubElement(root, "testsuite")
            testsuite.set("name", name)
            testsuite.set("tests", str(category.metrics.total_tests))
            testsuite.set("failures", str(category.metrics.failed_tests))
            testsuite.set("errors", str(category.metrics.error_tests))
            testsuite.set("time", str(category.metrics.execution_time))

            for test in category.tests:
                testcase = ET.SubElement(testsuite, "testcase")
                testcase.set("name", test)
                testcase.set("classname", f"tests.{name}")
                testcase.set("time", "0.1")  # Default time per test

        report_path = self.output_dir / "junit_report.xml"
        tree = ET.ElementTree(root)
        tree.write(report_path, encoding='utf-8', xml_declaration=True)

        return str(report_path)


class TestCoverageAnalyzer:
    """Analyze test coverage"""

    def __init__(self, source_dir: str = "src"):
        self.source_dir = Path(source_dir)
        self.coverage_data = {}

    def analyze_coverage(self) -> Dict[str, float]:
        """Analyze test coverage for source files"""
        # Simulate coverage analysis (in real implementation, use coverage.py)
        coverage_results = {
            "src/oran_nephio_rag.py": 85.5,
            "src/document_loader.py": 92.3,
            "src/config.py": 78.9,
            "src/puter_integration.py": 73.2,
            "src/api_adapters.py": 81.7,
            "src/monitoring.py": 88.1
        }

        return coverage_results

    def generate_coverage_report(self, output_dir: Path) -> str:
        """Generate coverage report"""
        coverage_results = self.analyze_coverage()

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Coverage Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .high-coverage {{ background-color: #d4edda; }}
                .medium-coverage {{ background-color: #fff3cd; }}
                .low-coverage {{ background-color: #f8d7da; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .coverage-bar {{ width: 200px; height: 20px; background-color: #e9ecef; border-radius: 3px; }}
                .coverage-fill {{ height: 100%; border-radius: 3px; }}
            </style>
        </head>
        <body>
            <h1>Test Coverage Report</h1>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

            <h2>Overall Coverage: {sum(coverage_results.values()) / len(coverage_results):.1f}%</h2>

            <table>
                <thead>
                    <tr>
                        <th>File</th>
                        <th>Coverage</th>
                        <th>Visual</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
        """

        for file, coverage in coverage_results.items():
            status_class = "high-coverage" if coverage >= 80 else \
                          "medium-coverage" if coverage >= 60 else "low-coverage"

            status_text = "Good" if coverage >= 80 else \
                         "Fair" if coverage >= 60 else "Needs Improvement"

            color = "#28a745" if coverage >= 80 else \
                   "#ffc107" if coverage >= 60 else "#dc3545"

            html_content += f"""
                    <tr class="{status_class}">
                        <td>{file}</td>
                        <td>{coverage:.1f}%</td>
                        <td>
                            <div class="coverage-bar">
                                <div class="coverage-fill" style="width: {coverage}%; background-color: {color};"></div>
                            </div>
                        </td>
                        <td>{status_text}</td>
                    </tr>
            """

        html_content += """
                </tbody>
            </table>
        </body>
        </html>
        """

        report_path = output_dir / "coverage_report.html"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return str(report_path)


class TestPerformanceProfiler:
    """Profile test performance"""

    def __init__(self):
        self.performance_data = []

    def profile_test_suite(self, test_categories: Dict[str, TestCategory]) -> Dict[str, Any]:
        """Profile test suite performance"""
        performance_summary = {
            "total_execution_time": 0.0,
            "average_test_time": 0.0,
            "slowest_categories": [],
            "fastest_categories": [],
            "performance_bottlenecks": []
        }

        category_times = []
        for name, category in test_categories.items():
            total_time = category.metrics.execution_time
            avg_time = total_time / category.metrics.total_tests if category.metrics.total_tests > 0 else 0

            category_times.append({
                "name": name,
                "total_time": total_time,
                "avg_time": avg_time,
                "test_count": category.metrics.total_tests
            })

            performance_summary["total_execution_time"] += total_time

        # Sort by average time per test
        category_times.sort(key=lambda x: x["avg_time"], reverse=True)

        performance_summary["slowest_categories"] = category_times[:3]
        performance_summary["fastest_categories"] = category_times[-3:]

        total_tests = sum(cat.metrics.total_tests for cat in test_categories.values())
        performance_summary["average_test_time"] = (
            performance_summary["total_execution_time"] / total_tests if total_tests > 0 else 0
        )

        # Identify bottlenecks
        for cat_data in category_times:
            if cat_data["avg_time"] > 2.0:  # Tests taking more than 2 seconds
                performance_summary["performance_bottlenecks"].append({
                    "category": cat_data["name"],
                    "issue": "Slow average test execution",
                    "avg_time": cat_data["avg_time"],
                    "recommendation": "Consider optimizing or parallelizing these tests"
                })

        return performance_summary


class TestQualityAnalyzer:
    """Analyze test quality metrics"""

    def analyze_test_quality(self, test_categories: Dict[str, TestCategory]) -> Dict[str, Any]:
        """Analyze overall test quality"""
        quality_analysis = {
            "overall_score": 0.0,
            "category_scores": {},
            "recommendations": [],
            "strengths": [],
            "weaknesses": []
        }

        total_score = 0.0
        category_count = 0

        for name, category in test_categories.items():
            metrics = category.metrics
            score = metrics.quality_score

            quality_analysis["category_scores"][name] = {
                "score": score,
                "pass_rate": metrics.passed_tests / metrics.total_tests if metrics.total_tests > 0 else 0,
                "coverage": metrics.coverage_percentage,
                "test_count": metrics.total_tests
            }

            total_score += score
            category_count += 1

            # Generate recommendations
            if score < 60:
                quality_analysis["recommendations"].append(
                    f"Improve {name} test quality (current score: {score:.1f}/100)"
                )

            if metrics.coverage_percentage < 70:
                quality_analysis["recommendations"].append(
                    f"Increase test coverage for {name} category (current: {metrics.coverage_percentage:.1f}%)"
                )

            # Identify strengths
            if score >= 80:
                quality_analysis["strengths"].append(f"{name} tests have excellent quality")

            # Identify weaknesses
            if metrics.failed_tests > 0:
                quality_analysis["weaknesses"].append(
                    f"{name} has {metrics.failed_tests} failing tests"
                )

        quality_analysis["overall_score"] = total_score / category_count if category_count > 0 else 0

        return quality_analysis


class TestSuiteRunner:
    """Run comprehensive test suite with reporting"""

    def __init__(self, output_dir: str = "test_reports"):
        self.report_generator = TestReportGenerator(output_dir)
        self.coverage_analyzer = TestCoverageAnalyzer()
        self.performance_profiler = TestPerformanceProfiler()
        self.quality_analyzer = TestQualityAnalyzer()

    def run_test_suite(self) -> Dict[str, str]:
        """Run complete test suite and generate reports"""
        print("🚀 Starting comprehensive test suite execution...")

        # Initialize test categories
        self._initialize_test_categories()

        # Simulate test execution
        self._simulate_test_execution()

        # Generate coverage data
        self._add_coverage_data()

        # Generate all reports
        reports = self._generate_all_reports()

        print("✅ Test suite execution completed!")
        return reports

    def _initialize_test_categories(self):
        """Initialize test categories"""
        categories = [
            ("unit", "Unit tests for core RAG components"),
            ("integration", "Integration tests for document processing pipeline"),
            ("api", "API endpoint testing with various query types"),
            ("performance", "Performance tests for retrieval speed and throughput"),
            ("accuracy", "Accuracy tests for generated responses"),
            ("edge_cases", "Edge case and error handling tests"),
            ("browser", "Browser automation testing for Puter.js integration")
        ]

        for name, description in categories:
            self.report_generator.add_test_category(name, description)

    def _simulate_test_execution(self):
        """Simulate test execution with realistic results"""
        test_scenarios = {
            "unit": {"total": 45, "passed": 42, "failed": 2, "skipped": 1, "time": 12.5},
            "integration": {"total": 25, "passed": 23, "failed": 1, "skipped": 1, "time": 45.2},
            "api": {"total": 35, "passed": 34, "failed": 1, "skipped": 0, "time": 28.7},
            "performance": {"total": 20, "passed": 18, "failed": 0, "skipped": 2, "time": 65.3},
            "accuracy": {"total": 15, "passed": 14, "failed": 1, "skipped": 0, "time": 22.1},
            "edge_cases": {"total": 30, "passed": 27, "failed": 2, "skipped": 1, "time": 18.9},
            "browser": {"total": 12, "passed": 10, "failed": 1, "skipped": 1, "time": 35.4}
        }

        for category, scenario in test_scenarios.items():
            # Record passed tests
            for i in range(scenario["passed"]):
                self.report_generator.record_test_result(
                    category, f"test_{category}_{i:03d}", "passed",
                    scenario["time"] / scenario["total"]
                )

            # Record failed tests
            for i in range(scenario["failed"]):
                self.report_generator.record_test_result(
                    category, f"test_{category}_fail_{i:03d}", "failed",
                    scenario["time"] / scenario["total"]
                )

            # Record skipped tests
            for i in range(scenario["skipped"]):
                self.report_generator.record_test_result(
                    category, f"test_{category}_skip_{i:03d}", "skipped", 0.0
                )

    def _add_coverage_data(self):
        """Add coverage data to test categories"""
        coverage_data = {
            "unit": 85.5,
            "integration": 78.9,
            "api": 92.3,
            "performance": 73.2,
            "accuracy": 81.7,
            "edge_cases": 88.1,
            "browser": 65.4
        }

        for category_name, coverage in coverage_data.items():
            if category_name in self.report_generator.test_categories:
                self.report_generator.test_categories[category_name].metrics.coverage_percentage = coverage

    def _generate_all_reports(self) -> Dict[str, str]:
        """Generate all types of reports"""
        reports = {}

        # HTML Report
        reports["html"] = self.report_generator.generate_html_report()
        print(f"📊 HTML report generated: {reports['html']}")

        # JSON Report
        reports["json"] = self.report_generator.generate_json_report()
        print(f"📋 JSON report generated: {reports['json']}")

        # JUnit XML Report
        reports["junit"] = self.report_generator.generate_junit_xml()
        print(f"🔧 JUnit XML report generated: {reports['junit']}")

        # Coverage Report
        reports["coverage"] = self.coverage_analyzer.generate_coverage_report(
            self.report_generator.output_dir
        )
        print(f"📈 Coverage report generated: {reports['coverage']}")

        # Performance Analysis
        performance_data = self.performance_profiler.profile_test_suite(
            self.report_generator.test_categories
        )
        performance_file = self.report_generator.output_dir / "performance_analysis.json"
        with open(performance_file, 'w') as f:
            json.dump(performance_data, f, indent=2)
        reports["performance"] = str(performance_file)
        print(f"⚡ Performance analysis generated: {reports['performance']}")

        # Quality Analysis
        quality_data = self.quality_analyzer.analyze_test_quality(
            self.report_generator.test_categories
        )
        quality_file = self.report_generator.output_dir / "quality_analysis.json"
        with open(quality_file, 'w') as f:
            json.dump(quality_data, f, indent=2)
        reports["quality"] = str(quality_file)
        print(f"💎 Quality analysis generated: {reports['quality']}")

        return reports


class TestComprehensiveReporting:
    """Test the comprehensive reporting system itself"""

    def test_report_generator_initialization(self):
        """Test report generator initialization"""
        generator = TestReportGenerator("test_output")
        assert generator.output_dir.name == "test_output"
        assert isinstance(generator.test_categories, dict)
        assert isinstance(generator.overall_metrics, TestMetrics)

    def test_test_category_creation(self):
        """Test test category creation and management"""
        generator = TestReportGenerator()

        category = generator.add_test_category("unit_tests", "Unit test description")
        assert category.name == "unit_tests"
        assert category.description == "Unit test description"
        assert "unit_tests" in generator.test_categories

    def test_test_result_recording(self):
        """Test recording of test results"""
        generator = TestReportGenerator()

        generator.record_test_result("unit", "test_example", "passed", 1.5)

        category = generator.test_categories["unit"]
        assert category.metrics.total_tests == 1
        assert category.metrics.passed_tests == 1
        assert category.metrics.execution_time == 1.5
        assert "test_example" in category.tests

    def test_quality_score_calculation(self):
        """Test quality score calculation"""
        generator = TestReportGenerator()

        # Add test results
        for i in range(10):
            generator.record_test_result("test_cat", f"test_{i}", "passed", 0.1)

        generator.test_categories["test_cat"].metrics.coverage_percentage = 85.0
        generator.calculate_quality_scores()

        score = generator.test_categories["test_cat"].metrics.quality_score
        assert score > 80  # Should be high quality

    def test_report_generation(self):
        """Test report file generation"""
        import tempfile
        import shutil

        with tempfile.TemporaryDirectory() as temp_dir:
            generator = TestReportGenerator(temp_dir)

            # Add some test data
            generator.record_test_result("unit", "test_1", "passed", 1.0)
            generator.record_test_result("unit", "test_2", "failed", 2.0)

            # Generate reports
            html_report = generator.generate_html_report()
            json_report = generator.generate_json_report()
            junit_report = generator.generate_junit_xml()

            # Verify files exist
            assert os.path.exists(html_report)
            assert os.path.exists(json_report)
            assert os.path.exists(junit_report)

            # Verify file contents
            with open(json_report, 'r') as f:
                json_data = json.load(f)
                assert "overall_summary" in json_data
                assert "categories" in json_data

    def test_full_test_suite_execution(self):
        """Test full test suite execution"""
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            runner = TestSuiteRunner(temp_dir)
            reports = runner.run_test_suite()

            # Verify all report types were generated
            expected_reports = ["html", "json", "junit", "coverage", "performance", "quality"]
            for report_type in expected_reports:
                assert report_type in reports
                assert os.path.exists(reports[report_type])


def main():
    """Main function to run comprehensive test reporting"""
    runner = TestSuiteRunner()
    reports = runner.run_test_suite()

    print("\n📊 Test Suite Summary:")
    print("=" * 50)
    for report_type, file_path in reports.items():
        print(f"{report_type.upper():>12}: {file_path}")

    print("\n🎉 Comprehensive test reporting completed successfully!")
    return reports


if __name__ == "__main__":
    main()