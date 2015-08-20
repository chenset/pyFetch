from setuptools import setup, find_packages

setup(
    name="pyFetch",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'Flask',
        'Flask-compress',
        'requests',
        'pymongo',
        'gevent',
        'Tld',
    ],
)