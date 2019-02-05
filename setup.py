from distutils.core import setup

try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()

setup(
    name = 'cache-me',
    packages = ['cache_me'],
    version = '0.1',
    description = 'A simple decorator to cache the results of functions',
    author = 'daniyall',
    author_email = 'dev.daniyall@gmail.com',
    url = 'https://github.com/daniyall/cache_me',
    download_url = 'https://github.com/daniyall/cache_me/archive/0.1.tar.gz',
    keywords = ['cache', 'cachable', 'save', 'intermediate'],
    classifiers = [],
    python_requires=">=3",
    license="LICENSE",
    long_description=read_md('README.md'),
    install_requires=[
        "pandas",
        "pyarrow"
    ]
)
