flake:
	flake8 iob test

flake_verbose:
	flake8 iob test --show-pep8

test:
	run test

coverage:
	coverage erase
	coverage run --source=iob -m runscript.cli test
	coverage report -m

.PHONY: all build venv flake test vtest testloop cov clean doc
