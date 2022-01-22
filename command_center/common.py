"""
Common functions
"""

from typing import List

def convert_str_to_bytes(bytes_str: str) -> List[int]:
    list_bytes = []
    len_ = len(bytes_str)
    if len_ % 2 != 0:
        raise Exception('Not even number of chars')

    bytes_count = len_ // 2
    for i in range(bytes_count):
        start = i * 2
        end = start + 1
        list_bytes.append(int(bytes_str[start: end + 1], 16))
    return list_bytes


def convert_bytes_to_str(list_bytes: List[int]) -> str:
    """
    Convert list of bytes to hex uppercase str
    """
    return ''.join('%0.2X' % i for i in list_bytes)


def convert_int_to_bytes(int_value: int) -> List[int]:
    """
    Conver int to list of bytes
    """

    list_bytes = []

    int_value
    while int_value:
        byte_ = int_value & 0xFF
        int_value = int_value >> 8
        list_bytes.append(byte_)

    if not list_bytes:
        list_bytes.append(0)

    return reversed(list_bytes)
