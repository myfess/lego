"""
Custom lego framework
"""


from my_lego_protocol import get_int32_command
from lego_bluetooth import send_nxt_command
from common import convert_bytes_to_str


class Command:
    """
    Lego motor command
    """

    def __init__(self, mail_box, motor_value, power, direction: int = 1):
        self.mail_box = mail_box
        self.motor = motor_value
        self.power = power
        self.direction = direction

    def get_json_message(self):
        """
        Get message for C# server
        """
        int32_command = get_int32_command(self.motor, self.power, self.direction)
        list_bytes = send_nxt_command(self.mail_box, int32_command)
        hex_command = convert_bytes_to_str(list_bytes)

        return f'''
            {{
                "type": "nxt_command",
                "value": "{hex_command}"
            }}
        '''


def send_commands(queue, commands):
    """
    Send list of commands
    """

    for com in commands:
        queue.put_nowait(com.get_message())


def motor_command(queue, mail_box, motor, motor_power: int):
    """
    Add command to queue
    """

    queue.put_nowait(
        Command(
            mail_box,
            motor,
            motor_power,
            direction=1
        ).get_json_message()
    )
