# Makefile
install:
	pip install -r requirements.txt
	pip install .

run:
	harmony

format:
	black .

lint:
	flake8 .

test:
	pytest
