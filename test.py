import click
from functions import get_wan_ip
import socket
print socket.gethostbyname(socket.gethostname())

print get_wan_ip()

#
# @click.command()
# @click.option('--name', prompt='Your name',
#               help='The person to greet.')
# def hello(name):
#     """Simple program that greets NAME for a total of COUNT times."""
#     click.echo('Hello %s!' % name)
#
#
# if __name__ == '__main__':
#     hello()
#     print 123123