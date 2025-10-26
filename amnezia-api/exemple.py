import asyncio
import aiohttp
import os

async def add_user(secret,config_name_base, hostname, port, **kwargs):

    url = f"http://{hostname}:{port}/create"
    payload = {"name": config_name_base}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers={"X-API-Key": secret}) as resp:
                data = await resp.json()
                if resp.status == 200:
                    return data.get("vpn_key")
                else:
                    return f"API Error: {data.get('error')}"
    except Exception as e:
        return f"Connection error: {e}"

async def delete_user(secret, config_name_base, hostname, port, **kwargs):
    url = f"http://{hostname}:{port}/delete"
    payload = {"name": config_name_base}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers={"X-API-Key": secret}) as resp:
                print(f"Status: {resp.status}")
                try:
                    error = await resp.json()
                    print(f"Response: {error}")
                except:
                    text = await resp.text()
                    print(f"Raw response: {text}")
                return resp.status == 200
    except Exception as e:
        print(f"Exception: {e}")
        return False

async def get_key_info(secret,config_name_base, hostname, port, **kwargs):

    url = f"http://{hostname}:{port}/key/{config_name_base}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={"X-API-Key": secret}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("vpn_key")
                else:
                    return None
    except:
        return None



if __name__ == "__main__":
    test_result = asyncio.run(add_user('secret_key','username', 'ip', 8081))
    print(test_result)
    #test_result = asyncio.run(delete_user('secret_key','username', 'ip', 8081))
    #test_result = asyncio.run(get_key_info('secret_key','username', 'ip', 8081))

