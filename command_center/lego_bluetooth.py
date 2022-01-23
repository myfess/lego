"""
Lego Bluetooth protocol
"""

from typing import List, Dict
from my_lego_protocol import parse_int32_sensor_value


def send_nxt_command(mail_box: int, command: int) -> List[int]:
    """
    NXT Bluetoth mail box command
    """

    msg = _send_nxt_command(mail_box, command)
    msg_len = [len(msg), 0]
    return msg_len + msg


def _send_nxt_command(mail_box: int, command: int) -> List[int]:
    """
    NXT Bluetoth mail box command
    """

    msg = [0, 9, 0, 5, 0, 0, 0, 0, 0]
    msg[2] = mail_box - 1
    tmp = command
    for i in range(4):
        msg[4 + i] = tmp & 0xFF
        tmp = tmp >> 8
    return msg


def parse_msg(msg: List[int]) -> Dict:
    """
    Parse list of bytes
    """

    len_ = len(msg)

    if len_ < 2:
        return {
            'type': 'ERROR',
            'data': None
        }

    m_len = msg[0] + msg[1] * 256

    if len_ != m_len + 2:
        return {
            'type': 'ERROR',
            'data': None
        }

    if m_len == 3 and msg[2] == 2 and msg[3] == 9 and msg[4] == 0:
        return {
            'type': 'VALUE_SENT',
            'data': None
        }

    if m_len == 9 and msg[2] == 128 and msg[3] == 9 and msg[5] == 5 and msg[10] == 0:
        value32 = 0

        for i in range(3, -1, -1):
            value32 = value32 << 8
            value32 |= msg[6 + i]

        return {
            'type': 'SENSOR_DATA',
            'data': parse_int32_sensor_value(value32)
        }

    return {
        'type': 'UNKNOWN',
        'data': None
    }
