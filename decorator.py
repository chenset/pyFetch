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
        # if url.find('273.cn') != -1:
        app.crawl(url)

    return {
        'ddd': 111,
    }


app.run(page)