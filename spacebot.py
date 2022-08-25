
import base64
import json
import logging
from typing import Union

from space_requests import make_request


class SpaceBot:
    def __init__(self, base_url, bot_id, bot_secret):
        self.id = bot_id
        self.secret = bot_secret
        self.url = base_url
        self.token = None
        self.project_info = None
        self.tags = None
        self.boards = None
        self.project_statuses = None

    @classmethod
    async def rise(cls, base_url, bot_id, bot_secret, main_project: Union[str, None] = None):
        bot = SpaceBot(base_url, bot_id, bot_secret)
        await bot.auth()
        if main_project:
            await bot.get_project_id(main_project)
            await bot.get_tags()
            await bot.get_issues_boards()
            await bot.get_project_statuses(bot.project_info["id"])
        return bot

    async def auth(self):
        secret = base64.b64encode(f'{self.id}:{self.secret}'.encode('ascii')).decode('utf-8')
        url = f'{self.url}/oauth/token'
        data = {
            'grant_type': 'client_credentials',
            'scope': '**'
        }
        headers = {
            'Authorization': f'Basic {secret}',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        auth = await make_request(url, 'post', headers, data)
        self.token = auth['access_token']
        return auth['access_token']

    async def send_message(self, channel_name, text):
        url = f'{self.url}/api/http/chats/messages/send-message'
        data = json.dumps(
            {"content": {
                "className": "ChatMessage.Text",
                "text": text
            },
                "channel": f"channel:name:{channel_name}"
            })
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        await make_request(url, 'post', headers, data)

    async def get_tags(self):
        url = f'{self.url}/api/http/projects/{self.project_info["id"]}/planning/tags'
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        self.tags = (await make_request(url, 'get', headers))['data']

    async def get_project_id(self, project_name):
        url = f'{self.url}/api/http/projects'
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        all_projects = await make_request(url, 'get', headers)
        for project in all_projects['data']:
            if project['name'] == project_name:
                self.project_info = project
        if self.project_info is None:
            raise Exception("Can't locate project with given name.")

    async def get_issues_boards(self):
        url = f'{self.url}/api/http/projects/{self.project_info["id"]}/planning/boards'
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        self.boards = (await make_request(url, 'get', headers))['data']

    async def get_issues_from_board(self, board_name):
        board_id = str()
        for board in self.boards:
            if board['name'] == board_name:
                board_id = board['id']
                break
        if board_id:
            url = f'{self.url}/api/http/projects/planning/boards/{board_id}/issues'
        else:
            print('There is no such board')
            return
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        issues_list = (await make_request(url, 'get', headers))['data']
        return issues_list

    async def get_all_issues(self):
        url = f'{self.url}/api/http/projects/id:{self.project_info["id"]}/planning/issues?sorting=CREATED&descending=true'
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        issues_list = (await make_request(url, 'get', headers))['data']
        return issues_list

    async def create_new_tag(self, tag_name: str, project_name: Union[str, None] = None):
        if project_name and project_name != self.project_info["name"]:
            proj = project_name
            bot = await SpaceBot.rise(self.url, self.id, self.secret, proj)
            newtag = await bot.create_new_tag(tag_name)
        else:
            url = f"{self.url}/api/http/projects/{self.project_info['id']}/planning/tags"
            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
            data = json.dumps({
                'path': [tag_name]
            })
            newtag = await make_request(url, 'post', headers, data)
        return newtag

    async def update_issue_tag(self, issue_number, tag_name, board_name: Union[str, None] = None):
        if self.project_info is None:
            raise Exception('No main project is found!')
        if board_name:
            issues = await self.get_issues_from_board(board_name)
        else:
            issues = await self.get_all_issues()
        issue_id, tag_id = str(), str()
        for issue in issues:
            if issue['number'] == issue_number:
                issue_id = issue['id']
                break
        for tag in self.tags:
            if tag['name'] == tag_name:
                tag_id = tag['id']
                break
        if not tag_id:
            newtag = await self.create_new_tag(tag_name)
            tag_id = newtag["id"]
        if issue_id and tag_id:
            url = f'{self.url}/api/http/projects/{self.project_info["id"]}/planning/issues/{issue_id}/tags/{tag_id}'
            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {self.token}'
            }
            await make_request(url, 'post', headers)
        else:
            if issue_id:
                logging.error('There is no tag at this name')
            elif tag_id:
                logging.error(f'There is no issue number {issue_number} at board {board_name}')
            else:
                logging.error('Tag name and issue number are invalid!')

    async def base_board_info(self, board_id):
        url = f'{self.url}/api/http/projects/planning/boards/id:{board_id}?$fields=info(columns(columns(name))),id,name'
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        return await make_request(url, 'get', headers)

    async def get_project_statuses(self, project_id):
        url = f'{self.url}/api/http/projects/id:{project_id}/planning/issues/statuses?$fields=id,name'
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        self.project_statuses = await make_request(url, 'get', headers)

    async def update_issue_status(self, board_name, issue_number, status_name):
        board_id, status_id, issue_id = str(), str(), str()
        issues = await self.get_issues_from_board(board_name)
        for issue in issues:
            if issue['number'] == issue_number:
                issue_id = issue['id']
                break
        for board in self.boards:
            if board['name'] == board_name:
                board_id = board['id']
                break
        for status in self.project_statuses:
            if status['name'] == status_name:
                status_id = status['id']
        if board_id and status_id and issue_id:
            url = f'{self.url}/api/http/projects/{self.project_info["id"]}/planning/issues/id:{issue_id}'
            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {self.token}'
            }
            data = json.dumps({"status": status_id})
            await make_request(url, 'patch', headers, data)
