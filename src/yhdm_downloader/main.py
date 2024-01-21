from selenium import webdriver
from rich.logging import RichHandler
from rich.prompt import Prompt
import logging
from bs4 import BeautifulSoup
import sys
import os
import shutil
import time
from utils.transcode_util import transcode
from utils.download_util import download_m3u8


# 获取视频标题
def getVideoTitle(bs: BeautifulSoup) -> str:
    class_div_gohome = bs.find(class_="gohome")
    title = BeautifulSoup(str(class_div_gohome), "html.parser").find_all("a")[-1].text
    return title


# 下载视频文件
def download_video(browser: webdriver.Chrome, url: str, index: int, cwd: str):
    # 使用selenium获取番剧index.m3u8链接
    logger.info("正在下载第" + str(index) + "个视频")
    req = browser.get(url)
    logger.info("等待网页加载完成")
    time.sleep(3)
    logger.info("开始解析")
    try:
        bs = BeautifulSoup(browser.page_source, "html.parser")
        class_iframe = bs.find("iframe")
        video_src = BeautifulSoup(str(class_iframe), "html.parser").iframe.attrs["src"]
        index_m3u8_url = video_src.split("url=")[1].replace("%3A", ":").replace("%2F", "/")
        # 获取标题
        title = getVideoTitle(bs=bs)
        logger.info("解析完成")
    except IndexError:
        logger.error("解析错误")
    # 开始下载.ts文件
    try:
        os.mkdir(os.path.join(cwd, "tmp"))
        logger.info("开始下载")
    except FileExistsError:
        # 错误处理
        logger.error("tmp文件已存在，正在删除tmp文件夹重试")
        shutil.rmtree(os.path.join(cwd, "tmp"))
        os.mkdir(os.path.join(cwd, "tmp"))
        logger.info("开始下载")
    download_m3u8(index_m3u8_url=index_m3u8_url, cwd=cwd)
    logger.info("下载完成，开始使用ffmpeg进行转码")
    # 开始使用ffmpeg进行转码
    # 将所有.ts文件的位置写入file_list.txt
    with open(os.path.join(cwd, "file_list.txt"), "w") as f:
        for file in os.listdir(os.path.join(cwd, "tmp")):
            f.write("file " + os.path.join(cwd, "tmp", file).replace("\\", "/") + "\n")
    # 生成ffmpeg运行命令
    if transcode(output_file_name=f"{title}-第{index}集.mp4"):
        logger.info("转码完成，正在清理临时文件")
    else:
        logger.error("转码失败，正在清理临时文件")
    # 清理tmp文件夹及生成的file_list.txt
    shutil.rmtree(os.path.join(cwd, "tmp"))
    os.remove(os.path.join(cwd, "file_list.txt"))
    # 输出结束
    logger.info("清理完毕")


# 主程序入口
if __name__ == "__main__":
    # 获取运行参数
    sys_argvs = sys.argv
    # 获取工作目录
    sys_cwd = os.getcwd()
    # 初始化控制台
    logging.basicConfig(
        level="INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )
    logger = logging.getLogger("rich")
    # 初始化浏览器
    browser_options = webdriver.ChromeOptions()
    browser_options.add_argument("--headless")
    browser_options.add_argument("--disable-gpu")
    browser_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    browser_options.add_argument("log-level=3")
    browser = webdriver.Chrome(options=browser_options)
    logger.info("浏览器加载成功")
    # 开始进行下载
    if len(sys_argvs) == 1:  # 如果没有运行参数，进入交互式程序
        url = input("请输入你要下载的番剧第一集的url地址 -> ")
        down_num = input("请输入要下载的集数 -> ").split('-')
        start_index = int(down_num[0])
        end_index = int(down_num[1])
    else:  # 如果有运行参数，直接获取url和下载集数
        try:
            url = sys_argvs[1]
            down_num = sys_argvs[2].split('-')
            start_index = int(down_num[0])
            end_index = int(down_num[1])
        except IndexError:
            logger.error("您输入的运行参数有误")
            exit()
    for i in range(end_index-start_index+1):
        list_url = list(url)
        list_url[-6] = str(int(list_url[-6]) + i + start_index)  # 修改url中的集数
        download_video(browser=browser, url="".join(list_url), index=i + start_index, cwd=sys_cwd)
    logger.info("下载完成")
    browser.quit()