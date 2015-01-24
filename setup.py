from setuptools import setup, find_packages
import os

ROOT = os.path.dirname(os.path.realpath(__file__))
version = '0.0.1'

setup(
    name = 'iob',
    version = version,
    description = 'Site Scraping Framework',
    author = 'Gregory Petukhov',
    author_email = 'lorien@lorien.name',

    packages = find_packages(),

    license = "MIT",
    classifiers = (
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP',
    ),
)
