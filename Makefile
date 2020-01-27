.PHONY: clean clean_pyc test develop conda-develop flake8 demo

BUILD=_build

clean:
	python jupytab/setup.py clean
	python jupytab-utils/setup.py clean

clean_pyc:
	find . -name '*.pyc' -deletemake test

conda-develop_jupytab:
	conda install -y --file jupytab/requirements-dev.txt
	conda install -y --file jupytab/requirements.txt
	(cd jupytab && python setup.py develop --no-deps)

conda-develop_jupytab-utils:
	conda install -y --file jupytab-utils/requirements-dev.txt
	conda install -y --file jupytab-utils/requirements.txt
	(cd jupytab-utils && python setup.py develop --no-deps)

conda-develop:
	$(MAKE) conda-develop_jupytab-utils
	$(MAKE) conda-develop_jupytab

samples-kernel:
	ipython kernel install --name jupytab-demo --user

test_jupytab:
	pytest ./jupytab/tests --junitxml=_build/tests/results.xml

test_jupytab-utils:
	pytest ./jupytab-utils/tests --junitxml=_build/tests/results.xml

test:
	$(MAKE) test_jupytab-utils
	python -m ipykernel install --user --name jupytab-demo
	$(MAKE) test_jupytab

flake8_jupytab-utils:
	flake8 ./jupytab-utils

flake8_jupytab:
	flake8 ./jupytab

flake8:
	$(MAKE) flake8_jupytab-utils
	$(MAKE) flake8_jupytab

demo:
	python -m ipykernel install --user --name jupytab-demo
	python -m jupytab --config ./tests/data/config.ini
