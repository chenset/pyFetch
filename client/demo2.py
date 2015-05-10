from spider import start
import time
import re


def page(spider):
    patt = r'<a[^>]+href="([(\.|h|/)][^"]+jandan[^"]+)"[^>]*>[^<]+</a>'
    r = re.compile(patt)
    match = r.findall(spider.html)
    time.sleep(5)
    for url in match:
        spider.crawl(url)

    title_patt = r'<title[^>]*>([^<]*)</title>'
    title_r = re.compile(title_patt)
    title_match = title_r.findall(spider.html)
    title = ''
    if title_match:
        title = title_match[0]

    return {
        'title': title,
        'ddd': 2222323,
    }


start('test.net', page)

