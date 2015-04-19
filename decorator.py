from spider import Spider

app = Spider()


@app.start
def start():
    app.crawl('http://www.douban.com')


@app.page
def page():
    print 'page'


@app.save
def save():
    print 'save'


# app.run()

import gzip, zlib

s = [str(x) for x in xrange(10000)]
ss = '0' * 1000000
print len(ss)
print len(zlib.compress(ss, 5))
# print zlib.compress(ss, 1)
print zlib.decompress(zlib.compress(ss, 1))

