import asyncio
import logging
import re

from spacebot import SpaceBot
import os


async def main():
    bot = await SpaceBot.rise(os.environ.get('INPUT_ORGANISATION_URL'), os.environ.get('INPUT_APP_ID'),
                              os.environ.get('INPUT_APP_SECRET'), os.environ.get('INPUT_PROJECT'))
    if os.environ.get('INPUT_MESSAGE'):
        await bot.send_message(os.environ.get('INPUT_CHAT_TITLE'), os.environ.get('INPUT_MESSAGE'))
    issue_numbers, commit_titles = os.environ.get('INPUT_ISSUE_NUMBERS'), os.environ.get('INPUT_COMMITS_TITLES')
    if (issue_numbers or commit_titles) and os.environ.get('INPUT_TAG') and os.environ.get('INPUT_PROJECT'):
        iss_list = list()
        if issue_numbers:
            iss_list += [iss for iss in issue_numbers.split(" ")]
        if commit_titles:
            print('commi here')
            iss_list += map(int, [re.sub("[^0-9]", "", comm) for
                                  comm in [b for c in [a.split(" ") for
                                                       a in commit_titles.split(",")] for
                                           b in c if b] if re.sub("[^0-9]", "", comm)])
        for iss in iss_list:
            try:
                asyncio.create_task(bot.update_issue_tag(int(iss), os.environ.get('INPUT_TAG')))
            except Exception as ex:
                logging.error(ex)
    await asyncio.gather(*asyncio.all_tasks() - {asyncio.current_task()})
    print("::set-output name=result::Done!")


if __name__ == '__main__':
    asyncio.run(main())
