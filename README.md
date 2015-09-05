# pyFetch
基于python的分布式爬虫

### 安装mongoDB
https://www.mongodb.org/downloads
默认端口运行mongoDB

### 安装依赖
windows 下的 gevent 可能需要安装 Microsoft Visual C++ Compiler for Python 2.7 http://www.microsoft.com/en-us/download/confirmation.aspx?id=44266

    pip install requests
    pip install pymongo
    pip install flask
    pip install flask-compress
    pip install gevent
    pip install tld
    pip install click
### 执行
服务器

    python service.py

客服端

    python client.py

### 访问

    http://127.0.0.1


## Todo list

- 项目队列为空的处理, 如:队列已经跑完
- website char code
- 抓取频率控制
- 避免抓取非html类型
- 参数可配置化
- 历史列表的分页
- 结果页面的下载
- 50X页面 超时页面
- 尽量避免403, 学习禁爬虫原理: 如,请求带上referer
- slave 执行环境安全