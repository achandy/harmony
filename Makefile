# Makefile
install:
	pip install .

run:
	harmony

format:
	black .

lint:
	ruff check . --fix

test:
	pytest
