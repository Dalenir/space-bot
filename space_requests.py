import json
from json import JSONDecodeError

import aiohttp


async def make_request(url: str, method: str, headers, data=None):
    async with aiohttp.ClientSession() as session:
        valid = {'get', 'post', 'update', 'delete', 'patch'}
        if method not in valid:
            raise ValueError(f"results: status must be one of {valid}.")
        if method == 'post':
            async with session.post(url=url, data=data, headers=headers) as response:
                resp = await response.read()
                try:
                    return json.loads(resp)
                except JSONDecodeError:
                    print('There is no response')
                    return None
        elif method == 'get':
            async with session.get(url=url, data=data, headers=headers) as response:
                resp = await response.read()
                return json.loads(resp)
        elif method == 'patch':
            async with session.patch(url=url, data=data, headers=headers) as response:
                resp = await response.read()
                try:
                    return json.loads(resp)
                except JSONDecodeError:
                    print('There is no response')
                    return None
