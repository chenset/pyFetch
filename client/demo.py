from spider import start
import re


def page(spider):
    patt = r'<a[^>]+href="([(\.|h|/)][^"]+jandan[^"]+)"[^>]*>[^<]+</a>'
    r = re.compile(patt)
    match = r.findall(spider.html)
    for url in match:
        spider.crawl(url)
    return {
        'ddd': 111,
    }


start('jandan.net', page)

