import pytest
from utils import batch_generator

def test_batch_generator_exact_division():
    """測試可以被批次大小整除的情況。"""
    data = list(range(10))
    batches = list(batch_generator(data, 5))
    assert len(batches) == 2
    assert batches[0] == [0, 1, 2, 3, 4]
    assert batches[1] == [5, 6, 7, 8, 9]

def test_batch_generator_with_remainder():
    """測試最後一個批次有餘數的情況。"""
    data = list(range(7))
    batches = list(batch_generator(data, 3))
    assert len(batches) == 3
    assert batches[0] == [0, 1, 2]
    assert batches[1] == [3, 4, 5]
    assert batches[2] == [6]

def test_batch_generator_empty_input():
    """測試輸入為空列表的情況。"""
    data = []
    batches = list(batch_generator(data, 5))
    assert len(batches) == 0