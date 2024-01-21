from utils.download_util import multi_thread_download
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import requests


class www_dmyinghua_com:
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
            class_scripts = bs.find_all("iframe")
            video_src = (
                BeautifulSoup(str(class_scripts[-1]), "html.parser")
                .iframe.attrs["src"]
                .split("=")[1]
            )
            index_m3u8_url = video_src.replace("/\\", ":")
            return index_m3u8_url
        except IndexError and KeyError:
            return None

    def getVideoTitle(self, bs: BeautifulSoup) -> str:
        class_title = bs.find(class_="title")
        title = class_title.text
        return title

    def download_m3u8(self, index_m3u8_url: str, cwd: str) -> list:
        index_m3u8_lines = requests.get(index_m3u8_url).text.split("\n")
        mixed_m3u8_url = (
            "https://" + index_m3u8_url.split("/")[2] + index_m3u8_lines[-2]
        )
        mixed_m3u8 = requests.get(mixed_m3u8_url).text.split("\n")
        urls = []
        for ts_url in mixed_m3u8:
            if "#" not in ts_url and ts_url != "":
                urls.append(ts_url)
        multi_thread_download(urls)
        return urls
