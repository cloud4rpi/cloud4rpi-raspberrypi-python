.PHONY: init style lint test

init:
	pip install --upgrade -r requirements.txt

style:
	pep8 --show-source --show-pep8 .

lint:
	pylint --rcfile=.pylintrc --reports=n *.py test/*.py

test:
	python -m unittest discover test

ci: style lint test
