import asyncio
import logging

from spacebot import SpaceBot
import os


async def main():
    bot = await SpaceBot.rise(os.environ.get('INPUT_ORGANISATION_URL'), os.environ.get('INPUT_APP_ID'),
                              os.environ.get('INPUT_APP_SECRET'))
    bot.send_message(os.environ.get('INPUT_CHAT_TITLE'), os.environ.get('INPUT_MESSAGE'))
    print("::set-output name=result::Done!")


if __name__ == '__main__':
    asyncio.run(main())
