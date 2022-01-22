"""
NXT train logic
"""

import json
import asyncio
import datetime
from concurrent.futures.thread import ThreadPoolExecutor
from enum import IntEnum
from collections import defaultdict, deque
from lego_bluetooth import parse_msg, send_nxt_command
from common import convert_str_to_bytes, convert_int_to_bytes, convert_bytes_to_str
from my_lego_protocol import get_int32_command

HOST = '127.0.0.1'
PORT = 11000

MAIL_BOX = 1
MOTOR_A = 1
MOTOR_B = 2
COLOR_SENSOR_3 = 3

motor = False
# send = False


class SpeedStat:
    def __init__(self):
        self.queue = deque(maxlen=100)
        self.stat = defaultdict(int)

    def add_color(self, color):
        self.queue.append((datetime.datetime.now(), color))
        self.stat[color] += 1

    def get_stat(self):
        cnt = 0
        for color in self.stat:
            cnt += self.stat[color]

        if not cnt:
            return

        colors = []
        for color, color_cnt in self.stat.items():
            colors.append(f'{color}: {int(color_cnt * 100 / cnt)}')
        return ', '.join(colors)

    def get_speed(self) -> int:
        interval_seconds = 3
        time_interval = datetime.timedelta(seconds=interval_seconds)
        now_ = datetime.datetime.now()
        cnt = 0
        for dt, color in reversed(self.queue):
            interval_ = now_ - dt
            if interval_ > time_interval:
                break
            cnt += 1

        brick_size = 0.008
        brick_width = 2 # 2 stud
        sec_in_hour = 3600
        meters_in_hour = int(cnt * brick_size * brick_width * sec_in_hour / interval_seconds)
        return meters_in_hour


class PlateColor:
    """
    Detect color of plate
    """

    def __init__(self):
        self.color = None
        self.datetime = None

    def new_color(self, color):
        old_color = self.color
        old_datetime = self.datetime
        self.datetime = datetime.datetime.now()
        old_color = color
        color_time = self.datetime - old_datetime if old_datetime else 0
        return old_color, color_time


stat = SpeedStat()
plate = PlateColor()

class ServerCrash:
    pass


class Color(IntEnum):
    BLACK = 1 # ничего/черный
    BLUE = 2
    GREEN = 3
    YELLOW = 4
    RED = 5
    WHITE = 6


class Command:
    def __init__(self, motor, power, direction: int = 1):
        self.motor = motor
        self.power = power
        self.direction = direction

    # def get_message(self):
    #     return f'''
    #         {{
    #             "type": "nxt_command",
    #             "motor": {self.motor},
    #             "value": {self.power},
    #             "direction": {self.direction}
    #         }}
    #     '''

    def get_message(self):
        int32_command = get_int32_command(self.motor, self.power, self.direction)
        list_bytes = send_nxt_command(MAIL_BOX, int32_command)
        hex_command = convert_bytes_to_str(list_bytes)

        return f'''
            {{
                "type": "nxt_command",
                "value": "{hex_command}"
            }}
        '''

def stop_train():
    return [
        Command(MOTOR_A, power=0),
        Command(MOTOR_B, power=0)
    ]


def send_commands(queue, commands):
    for com in commands:
        queue.put_nowait(com.get_message())


def send_speed_to_gui(queue, speed: int):
    msg_speed = f'''
        {{
            "type": "gui",
            "speed": {speed}
        }}
    '''
    queue.put_nowait(msg_speed)


def handle_message(message, queue):
    global motor
    global stat
    global plate

    if message.get('type') == 'user_command':
        print(message)
        return

    if message.get('type') != 'nxt_message':
        return

    # print(message)
    bytes_list = convert_str_to_bytes(message['value'])
    msg = parse_msg(bytes_list)

    if msg['type'] != 'SENSOR_DATA':
        print(msg)
        return

    data = msg['data']

    if data['sensor'] == 5:
        return

    # print(data)

    if data['sensor'] == COLOR_SENSOR_3:
        color = data['value']
        stat.add_color(color)
        old_color, color_interval = plate.new_color(color)
        if old_color == Color.YELLOW:
            print(f'yellow interval: {color_interval}')
        # print(stat.get_stat())
        send_speed_to_gui(queue, stat.get_speed())

    if data['sensor'] == COLOR_SENSOR_3 and data['value'] == Color.YELLOW:
        # yellow tile - round end/start
        print(datetime.datetime.now())
        # send_commands(queue, stop_train())
        pass

    return


    # global motor, send
    if data['sensor'] == COLOR_SENSOR_3 and data['value'] == COLOR_RED:
        # print('!!!!!!')
        motor = not motor
        # send = True

        value = 100 if motor else 0
        # value = 0 if i % 2 else 100
        message = f'{{"motor": {MOTOR_A}, "value": {value}, "direction": 1}}'
        queue.put_nowait(message)


async def read_client(reader, queue):
    while True:
        try:
            data_bytes = await reader.read(100)
        except ConnectionResetError:
            print('Server crash')
            queue.put_nowait(ServerCrash())
            return

        msg_str = data_bytes.decode()
        if not msg_str:
            # Server crash
            print('Server crash')
            queue.put_nowait(ServerCrash())
            return
        # print(msg_str)
        # data = json.loads(msg_str)
        for data in parse_json_list(msg_str):
            handle_message(data, queue)


def parse_json_list(msgs: str):
    """
    Parse concatenated messages like this one:

    msgs = '{"sensor": 3, "value": 1}{"sensor": 3, "value": 6}'
    """

    start = 0
    for i, ch in enumerate(msgs):
        if ch == '}':
            next_start = i + 1
            msg = msgs[start:next_start]
            try:
                yield json.loads(msg)
            except Exception as e:
                print(f'ERROR: {msg}')
            start = next_start


async def write_client(writer, queue):
    # global motor, send

    # i = 0
    while True:
        msg = await queue.get()

        if isinstance(msg, ServerCrash):
            # Server crash
            return

        # await asyncio.sleep(1)
        # i += 1
        # if not send:
        #     continue
        # send = False
        # value = 100 if motor else 0
        # value = 0 if i % 2 else 100
        # message = f'{{"motor": {MOTOR_A}, "value": {value}, "direction": 1}}'
        # print('---------SEND--------')
        # writer.write(message.encode())
        # print(msg)
        writer.write(msg.encode())
        # print(message)
        # print(message.encode())
        queue.task_done()


def motor_command(loop, queue, motor_power: int):
    loop.call_soon_threadsafe(
        queue.put_nowait,
        Command(
            MOTOR_A,
            motor_power,
            direction=1
        ).get_message()
    )
    # loop.call_soon_threadsafe(
    #     queue.put_nowait,
    #     Command(MOTOR_B, motor_power, direction=1).get_message()
    # )
    # message_a = f'{{"motor": {MOTOR_A}, "value": {motor_power}, "direction": 1}}'
    # message_b = f'{{"motor": {MOTOR_B}, "value": {motor_power}, "direction": 1}}'
    # loop.call_soon_threadsafe(queue.put_nowait, message_a)
    # loop.call_soon_threadsafe(queue.put_nowait, message_b)


def console_input(loop, queue):
    global motor

    while True:
        line = input()
        print(f'command: {line}')
        if line == 's':
            motor_command(loop, queue, motor_power=100)
        elif line == 'e':
            motor_command(loop, queue, motor_power=0)
        elif line >= '0' and line <= '9' or line == '10':
            motor_power = int(line) * 10
            motor_command(loop, queue, motor_power=motor_power)


async def nxt_client():
    try:
        reader, writer = await asyncio.open_connection(HOST, PORT)
    except ConnectionRefusedError:
        print('Server is not ready')
        return

    print('connected')

    queue = asyncio.Queue()

    read_task = asyncio.create_task(read_client(reader, queue))
    write_task = asyncio.create_task(write_client(writer, queue))

    thread_pool_executor = ThreadPoolExecutor(1)
    console_task = asyncio.get_event_loop().run_in_executor(
        thread_pool_executor,
        console_input,
        asyncio.get_event_loop(),
        queue
    )

    await read_task
    await write_task

    print(1)
    writer.close()
    print(2)

    return

    # await console_task


async def main():
    await nxt_client()


def foo():
    asyncio.run(main())

foo()
