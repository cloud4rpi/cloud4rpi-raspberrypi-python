.PHONY: init style lint test

init:
	pip install --upgrade -r requirements.txt

style:
	pycodestyle --show-source --show-pep8 .

lint:
	pylint --rcfile=.pylintrc --reports=n *.py test/*.py

test:
	python -m unittest discover test

ci: style lint test
