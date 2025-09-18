"""
Performance tests for retrieval speed and throughput
Testing: Query response times, batch processing, concurrent operations, memory usage
"""

import os
import pytest
import time
import threading
import asyncio
import psutil
import gc
from unittest.mock import MagicMock, patch
from typing import List, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

from langchain.docstore.document import Document


@dataclass
class PerformanceMetrics:
    """Performance metrics container"""
    query_time: float
    memory_usage_mb: float
    cpu_percent: float
    throughput_qps: float
    success_rate: float
    avg_response_size: int


class TestQueryPerformance:
    """Test query processing performance"""

    @pytest.fixture
    def performance_config(self, temp_test_dir):
        """Performance-optimized configuration"""
        from src.config import Config

        config = Config()
        config.VECTOR_DB_PATH = os.path.join(temp_test_dir, "perf_vectordb")
        config.CHUNK_SIZE = 512
        config.CHUNK_OVERLAP = 100
        config.RETRIEVER_K = 5
        config.REQUEST_TIMEOUT = 10
        config.MAX_RETRIES = 1

        return config

    @pytest.fixture
    def mock_fast_rag_system(self, performance_config):
        """Fast mock RAG system for performance testing"""
        rag_system = MagicMock()
        rag_system.is_ready = True

        # Fast query responses
        def fast_query(question, **kwargs):
            return {
                "success": True,
                "answer": f"Fast response for: {question[:50]}...",
                "sources": [
                    {
                        "content": "Sample content for performance testing",
                        "metadata": {"source": "test", "type": "nephio"},
                        "similarity_score": 0.9
                    }
                ] * kwargs.get("k", 5),
                "query_time": 0.1,  # Simulated fast processing
                "context_used": kwargs.get("k", 5),
                "constraint_compliant": True
            }

        rag_system.query.side_effect = fast_query
        return rag_system

    @pytest.fixture
    def performance_queries(self):
        """Set of queries for performance testing"""
        return [
            "What is Nephio?",
            "How to scale O-RAN network functions?",
            "Explain Nephio architecture",
            "O-RAN integration procedures",
            "Network function deployment guide",
            "Kubernetes automation platform",
            "Intent-driven scaling strategies",
            "Multi-cluster management",
            "GitOps workflows in Nephio",
            "Edge deployment scenarios"
        ]

    def test_single_query_response_time(self, mock_fast_rag_system, performance_queries):
        """Test individual query response times"""
        response_times = []

        for query in performance_queries[:5]:  # Test subset for speed
            start_time = time.time()
            result = mock_fast_rag_system.query(query)
            end_time = time.time()

            response_time = end_time - start_time
            response_times.append(response_time)

            # Verify successful response
            assert result["success"] is True
            assert "answer" in result

            # Performance assertion
            assert response_time < 1.0  # Should respond within 1 second

        # Aggregate performance metrics
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)

        assert avg_response_time < 0.5  # Average should be under 500ms
        assert max_response_time < 1.0   # Maximum should be under 1 second

    def test_batch_query_throughput(self, mock_fast_rag_system, performance_queries):
        """Test batch query processing throughput"""
        batch_size = 10
        num_batches = 3

        total_queries = 0
        total_time = 0

        for batch_idx in range(num_batches):
            batch_start = time.time()

            # Process batch of queries
            for query in performance_queries:
                result = mock_fast_rag_system.query(query, k=3)
                assert result["success"] is True
                total_queries += 1

            batch_end = time.time()
            total_time += (batch_end - batch_start)

        # Calculate throughput
        queries_per_second = total_queries / total_time

        # Performance assertions
        assert queries_per_second > 5.0   # Should handle >5 QPS
        assert total_time < 10.0          # Total processing should be fast

    def test_concurrent_query_performance(self, mock_fast_rag_system, performance_queries):
        """Test concurrent query processing performance"""
        num_threads = 5
        queries_per_thread = 4
        results = []

        def process_queries(thread_id):
            thread_results = []
            for i in range(queries_per_thread):
                query = performance_queries[i % len(performance_queries)]

                start_time = time.time()
                result = mock_fast_rag_system.query(f"{query} (thread {thread_id})")
                end_time = time.time()

                thread_results.append({
                    "thread_id": thread_id,
                    "query_idx": i,
                    "response_time": end_time - start_time,
                    "success": result["success"]
                })

            return thread_results

        # Execute concurrent queries
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(process_queries, thread_id)
                for thread_id in range(num_threads)
            ]

            for future in as_completed(futures):
                results.extend(future.result())

        end_time = time.time()
        total_time = end_time - start_time

        # Verify all queries succeeded
        total_queries = len(results)
        successful_queries = sum(1 for r in results if r["success"])
        success_rate = successful_queries / total_queries

        assert success_rate >= 0.95  # 95% success rate
        assert total_queries == num_threads * queries_per_thread

        # Performance metrics
        avg_response_time = sum(r["response_time"] for r in results) / len(results)
        max_response_time = max(r["response_time"] for r in results)
        concurrent_qps = total_queries / total_time

        assert avg_response_time < 2.0    # Average response time under load
        assert max_response_time < 5.0    # Maximum response time
        assert concurrent_qps > 2.0       # Concurrent throughput

    @pytest.mark.slow
    def test_sustained_load_performance(self, mock_fast_rag_system, performance_queries):
        """Test performance under sustained load"""
        duration_seconds = 30
        target_qps = 3

        query_count = 0
        error_count = 0
        response_times = []

        start_time = time.time()
        end_time = start_time + duration_seconds

        while time.time() < end_time:
            query = performance_queries[query_count % len(performance_queries)]

            query_start = time.time()
            try:
                result = mock_fast_rag_system.query(query)
                query_end = time.time()

                response_times.append(query_end - query_start)

                if not result.get("success", False):
                    error_count += 1

            except Exception:
                error_count += 1

            query_count += 1

            # Rate limiting to maintain target QPS
            time.sleep(1.0 / target_qps)

        actual_duration = time.time() - start_time
        actual_qps = query_count / actual_duration
        error_rate = error_count / query_count if query_count > 0 else 1.0

        # Performance assertions
        assert actual_qps >= target_qps * 0.8  # Within 20% of target
        assert error_rate < 0.05               # Less than 5% error rate

        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            assert avg_response_time < 1.0     # Sustained performance


class TestVectorDatabasePerformance:
    """Test vector database operations performance"""

    @pytest.fixture
    def large_document_set(self):
        """Generate large document set for performance testing"""
        documents = []

        for i in range(100):  # 100 documents for performance testing
            content = f"""
            Document {i}: Nephio Network Function Management Performance Test

            This document contains comprehensive information about Nephio network function
            management, scaling strategies, and O-RAN integration for performance testing.

            Key topics include:
            - Kubernetes-based orchestration platform
            - Intent-driven automation workflows
            - Multi-cluster deployment strategies
            - Network function lifecycle management
            - GitOps configuration management
            - Performance monitoring and observability
            - Security and compliance frameworks
            - Cloud native ecosystem integration

            Document {i} provides detailed technical specifications and implementation
            guidelines for production deployments in telecom environments.
            """

            documents.append(Document(
                page_content=content,
                metadata={
                    "source": f"https://docs.nephio.org/perf-doc-{i}",
                    "type": "nephio",
                    "doc_id": i,
                    "content_length": len(content)
                }
            ))

        return documents

    @patch('src.oran_nephio_rag.HUGGINGFACE_EMBEDDINGS_AVAILABLE', False)
    @patch('src.oran_nephio_rag.SKLEARN_AVAILABLE', True)
    def test_vector_database_build_performance(self, performance_config, large_document_set):
        """Test vector database building performance"""
        from src.oran_nephio_rag import VectorDatabaseManager

        with patch('chromadb.Client'), patch('src.oran_nephio_rag.Chroma') as mock_chroma:
            mock_vectordb = MagicMock()
            mock_chroma.from_documents.return_value = mock_vectordb

            manager = VectorDatabaseManager(performance_config)

            # Measure build time
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB

            result = manager.build_vector_database(large_document_set)

            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB

            build_time = end_time - start_time
            memory_increase = end_memory - start_memory

            # Performance assertions
            assert result is True
            assert build_time < 30.0           # Should build within 30 seconds
            assert memory_increase < 500       # Memory increase should be reasonable

            # Verify chunking performance
            call_args = mock_chroma.from_documents.call_args
            if call_args:
                split_documents = call_args[1]["documents"]
                chunks_per_doc = len(split_documents) / len(large_document_set)
                assert chunks_per_doc < 10     # Reasonable chunking ratio

    def test_vector_search_performance(self, performance_config):
        """Test vector search performance"""
        from src.oran_nephio_rag import VectorDatabaseManager

        with patch('src.oran_nephio_rag.Chroma') as mock_chroma:
            # Setup fast search mock
            mock_vectordb = MagicMock()

            def fast_search(query, k=5):
                return [
                    (Document(
                        page_content=f"Fast search result {i} for {query}",
                        metadata={"source": f"test-{i}", "type": "nephio"}
                    ), 0.9 - i * 0.1)
                    for i in range(k)
                ]

            mock_vectordb.similarity_search_with_score.side_effect = fast_search
            mock_chroma.return_value = mock_vectordb

            manager = VectorDatabaseManager(performance_config)
            manager.vectordb = mock_vectordb

            # Test multiple searches
            search_queries = [
                "Nephio architecture",
                "O-RAN scaling",
                "Network function deployment",
                "Kubernetes automation",
                "Intent-driven management"
            ]

            search_times = []

            for query in search_queries:
                start_time = time.time()
                results = manager.search_similar(query, k=10)
                end_time = time.time()

                search_time = end_time - start_time
                search_times.append(search_time)

                # Verify results
                assert len(results) == 10
                assert all(score >= 0.0 for _, score in results)

                # Performance assertion
                assert search_time < 0.5  # Each search under 500ms

            # Aggregate performance
            avg_search_time = sum(search_times) / len(search_times)
            assert avg_search_time < 0.2  # Average under 200ms


class TestMemoryPerformance:
    """Test memory usage and optimization"""

    def get_memory_usage(self):
        """Get current memory usage in MB"""
        return psutil.Process().memory_info().rss / 1024 / 1024

    def test_memory_usage_during_processing(self, mock_fast_rag_system, performance_queries):
        """Test memory usage during query processing"""
        initial_memory = self.get_memory_usage()
        memory_readings = [initial_memory]

        # Process multiple queries and monitor memory
        for i, query in enumerate(performance_queries * 3):  # 30 queries total
            result = mock_fast_rag_system.query(query)
            assert result["success"] is True

            # Take memory reading every 5 queries
            if i % 5 == 0:
                current_memory = self.get_memory_usage()
                memory_readings.append(current_memory)

        final_memory = self.get_memory_usage()
        memory_readings.append(final_memory)

        # Memory analysis
        max_memory = max(memory_readings)
        memory_increase = max_memory - initial_memory

        # Performance assertions
        assert memory_increase < 100  # Memory increase should be < 100MB

        # Check for memory leaks (final should be close to initial)
        memory_retention = final_memory - initial_memory
        assert memory_retention < 50  # Should not retain > 50MB

    def test_memory_cleanup_after_batch_processing(self, mock_fast_rag_system, performance_queries):
        """Test memory cleanup after batch processing"""
        initial_memory = self.get_memory_usage()

        # Process large batch
        for _ in range(3):  # 3 batches
            for query in performance_queries:
                result = mock_fast_rag_system.query(query, k=10)  # Larger k for more memory usage
                assert result["success"] is True

        # Force garbage collection
        gc.collect()

        final_memory = self.get_memory_usage()
        memory_retained = final_memory - initial_memory

        # Memory should be released after batch processing
        assert memory_retained < 75  # Should not retain > 75MB after cleanup

    @pytest.mark.slow
    def test_long_running_memory_stability(self, mock_fast_rag_system, performance_queries):
        """Test memory stability over extended operation"""
        duration_seconds = 60  # 1 minute test
        memory_samples = []

        start_time = time.time()
        end_time = start_time + duration_seconds

        query_count = 0

        while time.time() < end_time:
            query = performance_queries[query_count % len(performance_queries)]
            result = mock_fast_rag_system.query(query)
            assert result["success"] is True

            query_count += 1

            # Sample memory every 10 queries
            if query_count % 10 == 0:
                memory_samples.append(self.get_memory_usage())

            time.sleep(0.1)  # Small delay to prevent overwhelming

        # Analyze memory stability
        if len(memory_samples) >= 2:
            initial_sample = memory_samples[0]
            final_sample = memory_samples[-1]
            max_sample = max(memory_samples)

            memory_growth = final_sample - initial_sample
            memory_peak = max_sample - initial_sample

            # Memory stability assertions
            assert memory_growth < 100     # Overall growth < 100MB
            assert memory_peak < 150      # Peak usage < 150MB increase


class TestThroughputBenchmarks:
    """Comprehensive throughput benchmarking"""

    @pytest.fixture
    def benchmark_rag_system(self):
        """RAG system optimized for benchmarking"""
        rag_system = MagicMock()
        rag_system.is_ready = True

        def benchmark_query(question, **kwargs):
            # Simulate realistic processing time
            time.sleep(0.05)  # 50ms simulated processing

            return {
                "success": True,
                "answer": f"Benchmark response for: {question[:30]}",
                "sources": [
                    {
                        "content": "Benchmark content",
                        "metadata": {"source": "benchmark", "type": "nephio"},
                        "similarity_score": 0.85
                    }
                ] * kwargs.get("k", 5),
                "query_time": 0.05,
                "context_used": kwargs.get("k", 5)
            }

        rag_system.query.side_effect = benchmark_query
        return rag_system

    def test_sequential_throughput_benchmark(self, benchmark_rag_system):
        """Benchmark sequential query throughput"""
        num_queries = 50
        test_query = "Benchmark query for sequential throughput testing"

        start_time = time.time()

        successful_queries = 0
        for i in range(num_queries):
            result = benchmark_rag_system.query(f"{test_query} {i}")
            if result.get("success", False):
                successful_queries += 1

        end_time = time.time()
        duration = end_time - start_time

        # Calculate metrics
        qps = successful_queries / duration
        success_rate = successful_queries / num_queries

        # Benchmark assertions
        assert success_rate >= 0.98    # 98% success rate
        assert qps >= 10               # At least 10 QPS sequential
        assert duration < 10           # Complete within 10 seconds

    def test_parallel_throughput_benchmark(self, benchmark_rag_system):
        """Benchmark parallel query throughput"""
        num_workers = 4
        queries_per_worker = 15
        total_queries = num_workers * queries_per_worker

        results = []

        def worker_queries(worker_id):
            worker_results = []
            for i in range(queries_per_worker):
                query = f"Parallel benchmark query {worker_id}-{i}"

                start_time = time.time()
                result = benchmark_rag_system.query(query)
                end_time = time.time()

                worker_results.append({
                    "worker_id": worker_id,
                    "query_id": i,
                    "success": result.get("success", False),
                    "response_time": end_time - start_time
                })

            return worker_results

        # Execute parallel benchmark
        benchmark_start = time.time()

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [
                executor.submit(worker_queries, worker_id)
                for worker_id in range(num_workers)
            ]

            for future in as_completed(futures):
                results.extend(future.result())

        benchmark_end = time.time()
        total_duration = benchmark_end - benchmark_start

        # Calculate parallel metrics
        successful_queries = sum(1 for r in results if r["success"])
        parallel_qps = successful_queries / total_duration
        success_rate = successful_queries / total_queries
        avg_response_time = sum(r["response_time"] for r in results) / len(results)

        # Parallel benchmark assertions
        assert success_rate >= 0.95      # 95% success rate under load
        assert parallel_qps >= 15        # Higher throughput with parallelism
        assert avg_response_time < 0.5   # Average response time under load

    def test_mixed_workload_benchmark(self, benchmark_rag_system):
        """Benchmark mixed workload performance"""
        # Define different query types with different complexities
        workload_types = [
            {"type": "simple", "k": 3, "weight": 0.5},
            {"type": "medium", "k": 5, "weight": 0.3},
            {"type": "complex", "k": 10, "weight": 0.2}
        ]

        total_queries = 60
        results = []

        start_time = time.time()

        for i in range(total_queries):
            # Select workload type based on weights
            import random
            rand = random.random()
            cumulative_weight = 0

            for workload in workload_types:
                cumulative_weight += workload["weight"]
                if rand <= cumulative_weight:
                    selected_workload = workload
                    break

            query = f"Mixed workload {selected_workload['type']} query {i}"

            query_start = time.time()
            result = benchmark_rag_system.query(query, k=selected_workload["k"])
            query_end = time.time()

            results.append({
                "query_id": i,
                "workload_type": selected_workload["type"],
                "k": selected_workload["k"],
                "success": result.get("success", False),
                "response_time": query_end - query_start
            })

        end_time = time.time()
        total_duration = end_time - start_time

        # Analyze mixed workload performance
        successful_queries = sum(1 for r in results if r["success"])
        mixed_qps = successful_queries / total_duration
        success_rate = successful_queries / total_queries

        # Performance by workload type
        for workload in workload_types:
            workload_results = [r for r in results if r["workload_type"] == workload["type"]]
            if workload_results:
                avg_response = sum(r["response_time"] for r in workload_results) / len(workload_results)
                print(f"{workload['type']} queries: {avg_response:.3f}s avg response time")

        # Mixed workload assertions
        assert success_rate >= 0.95      # 95% success rate
        assert mixed_qps >= 8            # Mixed workload throughput
        assert total_duration < 15       # Complete within reasonable time


class TestPerformanceRegression:
    """Performance regression testing"""

    def test_baseline_performance_metrics(self, mock_fast_rag_system):
        """Establish baseline performance metrics"""
        baseline_queries = [
            "What is Nephio architecture?",
            "How to scale O-RAN network functions?",
            "Network function deployment procedures"
        ]

        metrics = []

        for query in baseline_queries:
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024

            result = mock_fast_rag_system.query(query, k=5)

            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024

            metrics.append({
                "query": query,
                "response_time": end_time - start_time,
                "memory_delta": end_memory - start_memory,
                "success": result.get("success", False),
                "answer_length": len(result.get("answer", ""))
            })

        # Baseline performance thresholds
        for metric in metrics:
            assert metric["success"] is True
            assert metric["response_time"] < 1.0    # 1 second baseline
            assert metric["memory_delta"] < 10      # 10MB baseline
            assert metric["answer_length"] > 20     # Minimum answer quality

    def test_performance_under_stress(self, benchmark_rag_system):
        """Test performance degradation under stress"""
        stress_duration = 10  # 10 seconds of stress
        target_qps = 5

        query_times = []
        error_count = 0

        start_time = time.time()
        end_time = start_time + stress_duration

        query_count = 0

        while time.time() < end_time:
            query_start = time.time()

            try:
                result = benchmark_rag_system.query(f"Stress test query {query_count}")
                query_end = time.time()

                query_times.append(query_end - query_start)

                if not result.get("success", False):
                    error_count += 1

            except Exception:
                error_count += 1

            query_count += 1

            # Maintain stress rate
            time.sleep(max(0, (1.0 / target_qps) - (time.time() - query_start)))

        # Stress test analysis
        if query_times:
            avg_response_time = sum(query_times) / len(query_times)
            max_response_time = max(query_times)
            error_rate = error_count / query_count

            # Stress performance assertions
            assert avg_response_time < 2.0     # Average under stress
            assert max_response_time < 5.0     # Maximum under stress
            assert error_rate < 0.1            # Error rate under stress


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-m", "not slow"])