# pyspider
基于python的分布式爬虫

### 安装mongoDB
https://www.mongodb.org/downloads
默认端口运行mongoDB

### 安装依赖
    pip install requests
    pip install pymongo
    pip install flask
    pip install flask-compress
    pip install gevent
    pip install tld

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

