.PHONY: all flake flake_verbose test coverage clean upload

flake:
	flake8 crawler test script

flake_verbose:
	flake8 crawler test script --show-pep8

test:
	tox

coverage:
	coverage erase
	coverage run --source=crawler -m runscript.cli test
	coverage report -m

clean:
	find -name '*.pyc' -delete
	find -name '*.swp' -delete

upload:
	python setup.py sdist upload
