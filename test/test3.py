import os
import sys

import sys
import StringIO
import contextlib
import traceback


@contextlib.contextmanager
def stdoutIO(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO.StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old


code = """
print 'fsdfdsfds'
 i = [0,1,2]
for j in i :
    print j
"""
with stdoutIO() as s:
    try:
        exec code in {'fd': 1}
    except Exception, e:
        print e
        print traceback.format_exc()

print "out:" + s.getvalue() + '|'