import aiohttp
import asyncio
import os
import requests


# 下载任务
async def job(session: aiohttp.ClientSession, url: str, cwd: str):
    # 获取文件
    data = await session.get(url)
    data_code = await data.read()
    # 写入
    filename = os.path.join(cwd, "tmp", os.path.split(url)[-1])
    try:
        with open(filename, "wb") as f:
            f.write(data_code)
    except FileNotFoundError:
        pass


# 异步下载
async def download(loop: aiohttp.ClientSession.loop, urls: str, cwd: str):
    async with aiohttp.ClientSession() as session:
        tasks = [loop.create_task(job(session=session, url=_, cwd=cwd)) for _ in urls]
        finished, unfinished = await asyncio.wait(tasks)


# 下载m3u8文件
def download_m3u8(index_m3u8_url: str, cwd: str):
    # 生成mixed_m3u8文件位置
    mixed_m3u8_url = (
        index_m3u8_url.replace("index.m3u8", "")
        + requests.get(index_m3u8_url).text.split("\n")[-1]
    )
    # 下载mixed_m3u8
    mixed_m3u8 = requests.get(mixed_m3u8_url).text.split("\n")
    urls = []
    # 筛出ts文件地址
    for ts_url in mixed_m3u8:
        if "#" not in ts_url:
            urls.append(mixed_m3u8_url.replace("mixed.m3u8", "") + ts_url)
    # 调用异步下载函数进行并发下载
    loop = asyncio.new_event_loop()
    loop.run_until_complete(download(loop=loop, urls=urls, cwd=cwd))
    loop.close