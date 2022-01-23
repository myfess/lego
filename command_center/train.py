"""
Lego train app
"""

import datetime

from lego import Color
from common import convert_str_to_bytes
from lego_bluetooth import parse_msg
from train_speed import SpeedStat
from lego_tools import Command, motor_command


MAIL_BOX = 1
MOTOR_A = 1
MOTOR_B = 2
COLOR_SENSOR_3 = 3


class PlateColor:
    """
    Detect color of plate
    """

    def __init__(self):
        self.color = None
        self.datetime = None

    def new_color(self, color):
        """
        Handle new color
        """

        old_color = self.color
        old_datetime = self.datetime
        self.datetime = datetime.datetime.now()
        old_color = color
        color_time = self.datetime - old_datetime if old_datetime else 0
        return old_color, color_time


stat = SpeedStat()
plate = PlateColor()


def handle_message(message, queue):
    """
    Handle message from C# server
    """

    if message.get('type') == 'user_command':
        console_input(queue, message['value'])
        print(message)
        return

    if message.get('type') != 'nxt_message':
        return

    bytes_list = convert_str_to_bytes(message['value'])
    msg = parse_msg(bytes_list)

    if msg['type'] != 'SENSOR_DATA':
        print(msg)
        return

    data = msg['data']

    if data['sensor'] == 5:
        return

    if data['sensor'] == COLOR_SENSOR_3:
        color = data['value']
        stat.add_color(color)
        old_color, color_interval = plate.new_color(color)
        if old_color == Color.YELLOW:
            print(f'yellow interval: {color_interval}')
        send_speed_to_gui(queue, stat.get_speed())

    if data['sensor'] == COLOR_SENSOR_3 and data['value'] == Color.YELLOW:
        print(datetime.datetime.now())
        # send_commands(queue, stop_train())


def stop_train():
    """
    Get list of commands for stoping train
    """

    return [
        Command(MAIL_BOX, MOTOR_A, power=0),
        Command(MAIL_BOX, MOTOR_B, power=0)
    ]


def send_speed_to_gui(queue, speed: int):
    """
    Send speed to C# GUI
    """

    msg_speed = f'''
        {{
            "type": "gui",
            "speed": {speed}
        }}
    '''
    queue.put_nowait(msg_speed)


def console_input(queue, line):
    """
    Handle text command from C# GUI input field
    """

    while True:
        print(f'command: {line}')
        if line == 's':
            motor_command(queue, MAIL_BOX, MOTOR_A, motor_power=100)
        elif line == 'e':
            motor_command(queue, MAIL_BOX, MOTOR_A, motor_power=0)
        elif '0' <= line <= '9' or line == '10':
            motor_power = int(line) * 10
            motor_command(queue, MAIL_BOX, MOTOR_A, motor_power=motor_power)
