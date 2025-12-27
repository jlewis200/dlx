all: black pylint coverage

black:
	black ./

pylint:
	pylint --fail-under 9.5 ./

coverage:
	python3 -m coverage run --source . -m unittest
	python3 -m coverage report -m --fail-under 80

