import threading
import os
import requests
from requests.adapters import HTTPAdapter,Retry


def download_file(url):
    s = requests.Session()
    retries = Retry(total=99, backoff_factor=1, status_forcelist=[503])
    s.mount('https://', HTTPAdapter(max_retries=retries))
    with s.get(url, stream=True) as r:
        r.raise_for_status()
        with open(os.path.join(os.getcwd(), "tmp", url.split("/")[-1]), "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)


def multi_thread_download(urls: list):
    threads = []
    for i in range(8):
        for j in range(i, len(urls), 8):
            url = urls[j]
            thread = threading.Thread(target=download_file, args=(url,))
            thread.start()
            threads.append(thread)

    for thread in threads:
        thread.join()

        
