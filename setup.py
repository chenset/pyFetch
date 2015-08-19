from setuptools import setup, find_packages

setup(
    name="pyFetch",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'flask>=0.10',
    ],
)