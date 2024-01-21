from utils.download_util import multi_thread_download
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import requests


class www_iyhdmm_com:
    def getStartUrl(self, url: str, start_index: int) -> str:
        list_url = list(url)
        list_url[-6] = str(int(list_url[-6]) + start_index - 1)
        url = "".join(list_url)
        return url

    def getNextUrl(self, url: str) -> str:
        list_url = list(url)
        list_url[-6] = str(int(list_url[-6]) + 1)
        url = "".join(list_url)
        return url

    def getBsOfPage(self, url: str, browser: webdriver.Chrome) -> BeautifulSoup:
        req = browser.get(url)
        time.sleep(3)
        bs = BeautifulSoup(browser.page_source, "html.parser")
        return bs

    def getVideoIndexM3U8(self, bs: BeautifulSoup) -> str:
        try:
            class_iframe = bs.find("iframe")
            video_src = BeautifulSoup(str(class_iframe), "html.parser").iframe.attrs[
                "src"
            ]
            index_m3u8_url = (
                video_src.split("url=")[1].replace("%3A", ":").replace("%2F", "/")
            )
            return index_m3u8_url
        except IndexError:
            return None

    def getVideoTitle(self, bs: BeautifulSoup) -> str:
        class_div_gohome = bs.find(class_="gohome")
        title = (
            BeautifulSoup(str(class_div_gohome), "html.parser").find_all("a")[-1].text
        )
        return title

    def download_m3u8(self, index_m3u8_url: str, cwd: str):
        # 生成mixed_m3u8文件位置
        index_m3u8_lines = requests.get(index_m3u8_url).text.split("\n")
        mixed_m3u8_url = index_m3u8_url.replace("index.m3u8", "") + index_m3u8_lines[-1]
        # 下载mixed_m3u8
        mixed_m3u8 = requests.get(mixed_m3u8_url).text.split("\n")
        urls = []
        # 筛出ts文件地址
        for ts_url in mixed_m3u8:
            if "#" not in ts_url and ts_url != "":
                urls.append(mixed_m3u8_url.replace("mixed.m3u8", "") + ts_url)
        # 调用并发下载函数进行并发下载
        multi_thread_download(urls)
        return urls
