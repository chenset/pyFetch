from spider import Spider
import re
import time

app = Spider()


def page(html):
    # time.sleep(4)

    patt = r'<a[^>]+href="([(\.|h|/)][^"]+)"[^>]*>[^<]+</a>'

    r = re.compile(patt)
    match = r.findall(html)
    for url in match:
        app.crawl(url)

    return {
        'ddd': 111,
    }

app.run(page)

"""
'http://movie.douban.com/subject/23761370/',
'http://movie.douban.com/subject/23761360/',
'http://movie.douban.com/subject/23761350/',
'http://movie.douban.com/subject/23761340/',
'http://movie.douban.com/subject/23761330/',
'http://movie.douban.com/subject/23761320/',
'http://movie.douban.com/subject/23761310/',
'http://movie.douban.com/subject/23761380/',
'http://movie.douban.com/subject/23761390/',
"""