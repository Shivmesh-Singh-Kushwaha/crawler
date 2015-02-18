flake:
	flake8 iob test script

flake_verbose:
	flake8 iob test script --show-pep8

test:
	tox

coverage:
	coverage erase
	coverage run --source=iob -m runscript.cli test
	coverage report -m

clean:
	find -name '*.pyc' -delete
	find -name '*.swp' -delete

.PHONY: all build venv flake test vtest testloop cov clean doc
