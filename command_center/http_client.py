"""
HTTP client for C# lego server
"""

import asyncio

from common import parse_json_list


class ServerCrash:
    """
    C# server crash (not responding)
    """

    pass


async def nxt_client(host, port, handle_message_function):
    """
    Client for C# server connected to NXT
    """

    try:
        reader, writer = await asyncio.open_connection(host, port)
    except ConnectionRefusedError:
        print('Server is not ready')
        return

    print('connected')

    queue = asyncio.Queue()

    read_task = asyncio.create_task(read_client(reader, queue, handle_message_function))
    write_task = asyncio.create_task(write_client(writer, queue))

    await read_task
    await write_task

    writer.close()


async def read_client(reader, queue, handle_message_function):
    """
    Read messages from C# server
    """

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

        for data in parse_json_list(msg_str):
            handle_message_function(data, queue)


async def write_client(writer, queue):
    """
    Send messages to C# server
    """

    while True:
        msg = await queue.get()

        if isinstance(msg, ServerCrash):
            # Server crash
            return

        writer.write(msg.encode())
        queue.task_done()
