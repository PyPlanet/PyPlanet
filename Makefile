
build:
	@ python setup.py sdist
	@ python setup.py bdist_wheel --python-tag py3

publish:
	@ python setup.py sdist upload
	@ python setup.py bdist_wheel --python-tag py3 upload

run-tox:
	@ tox

run-nose:
	@ nosetests --nocapture .

tests: run-tox clean
tests-dev: run-nose clean

clean:
	@ find . -name '*.py[co]' -delete
	@ find . -name '__pycache__' -delete
	@ rm -rf *.egg-info dist build
