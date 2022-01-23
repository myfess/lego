"""
NXT train logic
"""

import asyncio
from http_client import nxt_client
from train import handle_message


HOST = '127.0.0.1'
PORT = 11000


async def main():
    """
    main async function
    """

    await nxt_client(HOST, PORT, handle_message)


def main_app():
    """
    Main function
    """

    asyncio.run(main())


main_app()
