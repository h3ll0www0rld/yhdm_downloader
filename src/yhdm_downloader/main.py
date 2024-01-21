from selenium import webdriver
from rich.logging import RichHandler
import logging
import sys
import os
import shutil
from utils.transcode_util import transcode
from templates.www_iyhdmm_com import www_iyhdmm_com
from templates.www_dmyinghua_com import www_dmyinghua_com


def download_video(browser, url, index, video_templates):
    # 使用selenium获取番剧index.m3u8链接
    logger.info("正在下载第" + str(index) + "个视频")
    logger.info("开始解析")
    bs = video_templates.getBsOfPage(url, browser)
    index_m3u8_url = video_templates.getVideoIndexM3U8(bs)
    if index_m3u8_url != None:
        logger.info("解析完成")
        try:
            os.mkdir(os.path.join(sys_cwd, "tmp"))
            logger.info("开始下载")
        except FileExistsError:
            # 错误处理
            logger.error("tmp文件已存在，正在删除tmp文件夹重试")
            shutil.rmtree(os.path.join(sys_cwd, "tmp"))
            os.mkdir(os.path.join(sys_cwd, "tmp"))
            logger.info("开始下载")
        # 开始下载.ts文件
        urls = video_templates.download_m3u8(index_m3u8_url=index_m3u8_url, cwd=sys_cwd)
        logger.info("下载完成，开始使用ffmpeg进行转码")
        # 开始使用ffmpeg进行转码
        # 将所有.ts文件的位置写入file_list.txt
        with open(os.path.join(sys_cwd, "file_list.txt"), "w") as f:
            f.truncate(0)
            for file in urls:
                f.write(
                    "file "
                    + os.path.join(sys_cwd, "tmp", file.split("/")[-1]).replace(
                        "\\", "/"
                    )
                    + "\n"
                )
        # 生成ffmpeg运行命令
        if transcode(
            output_file_name=f"{video_templates.getVideoTitle(bs)}-第{index}集.mp4"
        ):
            logger.info("转码完成，正在清理临时文件")
        else:
            logger.error("转码失败，正在清理临时文件")
        # 清理tmp文件夹及生成的file_list.txt
        shutil.rmtree(os.path.join(sys_cwd, "tmp"))
        os.remove(os.path.join(sys_cwd, "file_list.txt"))
        # 输出结束
        logger.info("清理完毕")
    else:
        logger.error("解析失败")


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
        handlers=[RichHandler(rich_tracebacks=True)],
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
        down_num = input("请输入要下载的集数 -> ").split("-")
        start_index = int(down_num[0])
        end_index = int(down_num[1])
    else:  # 如果有运行参数，直接获取url和下载集数
        try:
            url = sys_argvs[1]
            down_num = sys_argvs[2].split("-")
            start_index = int(down_num[0])
            end_index = int(down_num[1])
        except IndexError:
            logger.error("您输入的运行参数有误")
            exit()
    # 获取视频网站类型
    domain = url.split("/")[2]
    if domain == "www.iyhdmm.com":
        video_templates = www_iyhdmm_com()
    elif domain == "www.dmyinghua.com":
        video_templates = www_dmyinghua_com()
    else:
        logger.warning("网站不在支持名单上，将采用默认模版，可能会出现错误")
        video_templates = www_iyhdmm_com()
    url = video_templates.getStartUrl(url, start_index)
    for i in range(end_index - start_index + 1):
        download_video(
            browser=browser,
            url=url,
            index=i + start_index,
            video_templates=video_templates,
        )
        url = video_templates.getNextUrl(url)
    logger.info("下载完成")
    browser.quit()
