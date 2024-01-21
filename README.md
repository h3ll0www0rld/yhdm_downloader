# yhdm_downloader
## 一款基于Python的樱花动漫批量下载工具
## 支持的樱花动漫网站
已支持的有
```
https://www.iyhdmm.com/
https://www.dmyinghua.com # 不推荐，因为下载时会频繁报503错误，导致下载时间过长
```
其余可以通过阅读下面的`开发`部分自行适配
## 前置要求
安装pdm包管理器
## 运行
输入
```
git clone https://github.com/h3ll0www0rld/yhdm_downloader.git
cd yhdm_downloader
pdm install
```
运行
```
pdm start
```
启动程序  
或者你也可以输入
```
pdm start url down_num
```
直接进行下载，其中`url`为你想下载的番剧的第一集的播放url，`down_num`则为你想下载的集数范围  
示例：
```
pdm start https://www.iyhdmm.com/vp/22524-2-0.html 2-3
```
运行此命令将会下载《赛博朋克：边缘行者》的第2、3集  
如果您想下载单集，请将`down_num`改为`x-x`，其中x为集数  
示例：
```
pdm start https://www.iyhdmm.com/vp/22524-2-0.html 1-1
```
这将下载《赛博朋克：边缘行者》的第1集  
## 开发
输入
```
git clone https://github.com/h3ll0www0rld/yhdm_downloader.git
cd yhdm_downloader
pdm install
```
然后进入`templates`文件夹下，其中存放了各个网站的下载模版  
您可以模仿`example.py`，自行适配其他樱花动漫站点
