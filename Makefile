# Makefile
install:
	pip install -r requirements.txt
	pip install .

run:
	harmony

format:
	black .

lint:
	ruff check . --fix

test:
	pytest
