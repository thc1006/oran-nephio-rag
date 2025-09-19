from typing import Any, Iterator, List


def batch_generator(data: List[Any], batch_size: int) -> Iterator[List[Any]]:
    """一個將列表分割成指定大小批次的生成器。"""
    for i in range(0, len(data), batch_size):
        yield data[i : i + batch_size]
