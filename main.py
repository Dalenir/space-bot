import asyncio
import logging

from spacebot import SpaceBot
import os


async def main():
    try:
        bot = await SpaceBot.rise(os.environ.get('INPUT_ORGANISATION_URL'), os.environ.get('INPUT_APP_SECRET'),
                                  os.environ.get('INPUT_APP_SECRET'))
        bot.send_message(os.environ.get('INPUT_CHAT_TITLE'), os.environ.get('INPUT_MESSAGE'))
        print("::set-output name=result::Done!")
    except Exception as ex:
        logging.error(ex)


if __name__ == '__main__':
    asyncio.run(main())

