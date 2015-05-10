from spider import start
import re


def page(spider):
    patt = r'<a[^>]+href="([(\.|h|/)][^"]+jandan[^"]+)"[^>]*>[^<]+</a>'
    r = re.compile(patt)
    match = r.findall(spider.html)
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
        'ddd': 65464611,
    }


start('other.net', page)

