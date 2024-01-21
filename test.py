import requests

index_m3u8_url = 'https://leshiyuncdn.ahjunqin.top/20231201/b56CRrJP/index.m3u8'

mixed_m3u8_url = (
        index_m3u8_url.replace("index.m3u8", "")
        + requests.get(index_m3u8_url).text.split("\n")[-1]
    )

print(requests.get(index_m3u8_url).text.split("\n"))
print(mixed_m3u8_url)