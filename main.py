import asyncio
import logging

from spacebot import SpaceBot
import os


async def main():
    try:
        bot = await SpaceBot.rise(os.environ.get('INPUT_ORGANISATION_URL'), os.environ.get('INPUT_APP_ID'),
                                  os.environ.get('INPUT_APP_SECRET'), os.environ.get('INPUT_PROJECT'))
        if os.environ.get('INPUT_MESSAGE'):
            await bot.send_message(os.environ.get('INPUT_CHAT_TITLE'), os.environ.get('INPUT_MESSAGE'))
        if os.environ.get('INPUT_ISSUE_NUMBERS') and os.environ.get('INPUT_TAG') and os.environ.get('INPUT_PROJECT'):
            for iss in os.environ.get('INPUT_ISSUE_NUMBERS').replace("'", '').split(' '):
                print(iss)
                try:
                    asyncio.create_task(bot.update_issue_tag(int(iss), os.environ.get('INPUT_TAG')))
                except Exception as ex:
                    logging.error(ex)
        await asyncio.gather(*asyncio.all_tasks() - {asyncio.current_task()})
        print("::set-output name=result::Done!")
    except Exception as ex:
        logging.error(ex)

if __name__ == '__main__':
    asyncio.run(main())
