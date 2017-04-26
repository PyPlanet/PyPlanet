
build:
	@ python setup.py sdist
	@ python setup.py bdist_wheel --python-tag py3

publish:
	@ python setup.py sdist upload
	@ python setup.py bdist_wheel --python-tag py3 upload

run-tox:
	@ tox

test-unit:
	@ nosetests --rednose tests/unit

test-integration:
	@ nosetests --rednose tests/integration

tests: run-tox clean
tests-dev: run-nose clean

clean:
	@ find . -name '*.py[co]' -delete
	@ find . -name '__pycache__' -delete
	@ rm -rf *.egg-info dist build
