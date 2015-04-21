from spider import Spider

app = Spider()


def page(html):
    return {
        'ddd': 111,
    }


app.run(page)

