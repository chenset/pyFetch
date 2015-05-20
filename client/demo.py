from spider import start
import time
import re


def page(spider):
    for url in spider.urls:
        spider.crawl(url)

    title_patt = r'<title[^>]*>([^<]*)</title>'
    title_r = re.compile(title_patt)
    title_match = title_r.findall(spider.html)
    title = ''
    if title_match:
        title = title_match[0]

    return {
        'title': title,
        }


start('jandan', page)

