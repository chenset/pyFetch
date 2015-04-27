from spider import start
import re
import time


def page(spider):
    patt = r'<a[^>]+href="([(\.|h|/)][^"]+)"[^>]*>[^<]+</a>'
    r = re.compile(patt)
    match = r.findall(spider.html)
    for url in match:
        # if url.find('273.cn') != -1:
        spider.crawl(url)
    return {
        'ddd': 111,
    }


start(page)

