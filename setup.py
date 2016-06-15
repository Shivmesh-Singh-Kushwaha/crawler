from setuptools import setup, find_packages
import os

ROOT = os.path.dirname(os.path.realpath(__file__))

setup(
    name = 'crawler',
    version = '0.0.2',
    description = 'Web Scraping Framework based on py3 asyncio',
    long_description = open(os.path.join(ROOT, 'README.rst')).read(),
    author = 'Gregory Petukhov',
    author_email = 'lorien@lorien.name',
    install_requires = [
        'aiohttp',
    ],
    packages = find_packages(),
    license = "MIT",
    classifiers = [
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
