# yhdm_downloader
## 一款基于Python的樱花动漫批量下载工具
## 支持的樱花动漫网站
目前已知的有
```
https://www.iyhdmm.com/
```
其余等待验证
## 运行
输入
```
git clone https://github.com/h3ll0www0rld/yhdm_downloader.git
cd yhdm_downloader
pip install -r requirements.txt
```
您需要下载`ffmpeg`，并放在python程序目录下  
同时，您还需要配置`selenium`，本项目使用的是`chromedriver`，请自行进行安装并放在python程序目录下  
在完成上述内容后，运行
```
python main.py
```
以进入交互页面  
或者你也可以输入
```
python main.py url down_num
```
直接进行下载，其中`url`为你想下载的番剧的第一集的播放url，`down_num`则为你想下载的集数