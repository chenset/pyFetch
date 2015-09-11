# pyFetch
基于python的分布式爬虫

### 安装mongoDB
https://www.mongodb.org/downloads
默认端口运行mongoDB

### 安装依赖

linux 安装

    #ubuntu
    pip install python-dev
    #centos
    yum install python-devel


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

- 参数可配置化, 还有mongo的连接配置
- slave 执行环境安全
- setup.py
- 列表的时间排序有问题
- 每个项目都可以添加多个url抓取入口
- 项目与爬虫的抓取频率显示