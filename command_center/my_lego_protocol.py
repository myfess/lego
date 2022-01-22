"""
My own command protocol
"""

from typing import Dict


def get_int32_command(motor: int, power: int, direction: int) -> int:
    """
    0000AABB
        AA - motor number (1-4)
        BB - motor power (0 - 200)
    """

    return (motor << 8) + (100 + power * direction)


def parse_int32_sensor_value(value: int) -> Dict:
    """
    AAAABBBB
        AAAA - sensor number
        BBBB - sensor value
    """

    return {
        'sensor': (value >> 16) & 0xFFFF,
        'value': value & 0xFFFF
    }
