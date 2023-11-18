import os

try:
    from setuptools import setup, find_packages

    setup  # workaround for pyflakes issue #13
except ImportError:
    from distutils.core import setup
    
try:
    import multiprocessing

    multiprocessing
except ImportError:
    pass


def open_file(fname):
    return open(os.path.join(os.path.dirname(__file__), fname))


setup(
    name='example',
    version='0.1dev0',
    author='Author Name', 
    author_email='author_email@mail.com',
    packages=find_packages(),
    long_description=open('README.md').read()
)