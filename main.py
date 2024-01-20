from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import sys
import os
import requests
import aiohttp
import asyncio
import shutil
import time


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


# 获取视频标题
def getVideoTitle(bs: BeautifulSoup) -> str:
    class_div_gohome = bs.find(class_="gohome")
    title = BeautifulSoup(str(class_div_gohome), "html.parser").find_all("a")[-1].text
    return title


# 下载视频文件
def download_video(browser: webdriver.Chrome, url: str, index: int, cwd: str):
    # 使用selenium获取番剧index.m3u8链接
    print("正在下载第" + str(index) + "个视频")
    req = browser.get(url)
    print("等待网页加载完成")
    time.sleep(3)
    print("开始解析")
    bs = BeautifulSoup(browser.page_source, "html.parser")
    class_iframe = bs.find("iframe")
    video_src = BeautifulSoup(str(class_iframe), "html.parser").iframe.attrs["src"]
    index_m3u8_url = video_src.split("url=")[1].replace("%3A", ":").replace("%2F", "/")
    # 获取标题
    title = getVideoTitle(bs=bs)
    print("解析完成，开始下载")
    # 开始下载.ts文件
    os.mkdir(os.path.join(cwd, "tmp"))
    download_m3u8(index_m3u8_url=index_m3u8_url, cwd=cwd)
    print("下载完成，开始使用ffmpeg进行转码")
    # 开始使用ffmpeg进行转码
    # 将所有.ts文件的位置写入file_list.txt
    with open(os.path.join(cwd, "file_list.txt"), "w") as f:
        for file in os.listdir(os.path.join(cwd, "tmp")):
            f.write("file " + os.path.join(cwd, "tmp", file).replace("\\", "/") + "\n")
    # 生成ffmpeg运行命令
    ffmpeg_command = f".\\ffmpeg.exe -f concat -safe 0 -i .\\file_list.txt -c copy .\\{title}-第{index}集.mp4"
    os.system(ffmpeg_command.replace("\\", "\\\\"))
    print("转码完成，正在清理临时文件")
    # 清理tmp文件夹及生成的file_list.txt
    shutil.rmtree(os.path.join(cwd, "tmp"))
    os.remove(os.path.join(cwd, "file_list.txt"))
    # 输出结束
    print("清理完毕")


# 主程序入口
if __name__ == "__main__":
    # 获取运行参数
    sys_argvs = sys.argv
    # 获取工作目录
    sys_cwd = os.getcwd()
    # 初始化浏览器
    browser_options = webdriver.ChromeOptions()
    browser_options.add_argument("--headless")
    browser_options.add_argument("--disable-gpu")
    browser_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    browser_options.add_argument("log-level=3")
    browser = webdriver.Chrome(
        service=Service("chromedriver.exe"), options=browser_options
    )
    print("浏览器加载成功")
    # 开始进行下载
    if len(sys_argvs) == 1:  # 如果没有运行参数，进入交互式程序
        url = input("请输入你要下载的番剧第一集的url地址 -> ")
        down_num = int(input("请输入要下载的集数 -> "))
    else:  # 如果有运行参数，直接获取url和下载集数
        try:
            url = sys_argvs[1]
            down_num = int(sys_argvs[2])
        except IndexError:
            print("您输入的运行参数有误")
            exit()
    for i in range(down_num):
        list_url = list(url)
        list_url[-6] = str(int(list_url[-6]) + i)  # 修改url中的集数
        download_video(browser=browser, url="".join(list_url), index=i + 1, cwd=sys_cwd)
