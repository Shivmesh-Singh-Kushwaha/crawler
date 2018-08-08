Installation
============

To create virtual environment and install all dependencies run::

    make build

You can change dependencies in project/requirements.txt


Usage
=====

To launch scraping process run::

    crawl <crawler_class_name>

where <crawler_class_name> is just name of your crawler class.

At the moment crawler file should be in `crawlers/` package. That means
the `crawlers/` directory must have empty __init__.py file.


Database
========

By default the project is configured to use MongoDB, to change mongodb
connection settings and database name change MONGODB_CONNECTION and 
MONGODB_NAME in the project/settings.py


Support
=======

Email: lorien@lorien.name
Crawler project: http://github.com/lorien/crawler
