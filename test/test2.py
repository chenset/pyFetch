import ast
import inspect
import compiler.ast


# for i in inspect.getmembers(compiler.ast):
# print i


# for i in inspect.getmembers(__builtins__):
# print i

# print ast.NodeVisitor


ccc = """
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
        'ddd': 111,
    }


start('jandan.net', page)
"""


def loop(node):
    for child in node.getChildNodes():
        print child.__class__.__name__
        loop(child)


nodes = compiler.parse(ccc)
loop(nodes)