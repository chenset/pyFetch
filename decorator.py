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


app.run()


