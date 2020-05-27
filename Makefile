.PHONY: clean clean_pyc test develop conda-develop flake8 demo

BUILD=_build

clean:
	python jupytab-server/setup.py clean
	python jupytab/setup.py clean

clean_pyc:
	find . -name '*.pyc' -deletemake test

conda-develop_jupytab-server:
	conda install -y --file jupytab-server/requirements-dev.txt
	conda install -y --file jupytab-server/requirements.txt
	(cd jupytab-server && python setup.py develop --no-deps)

conda-develop_jupytab:
	conda install -y --file jupytab/requirements-dev.txt
	conda install -y --file jupytab/requirements.txt
	(cd jupytab && python setup.py develop --no-deps)

conda-develop:
	$(MAKE) conda-develop_jupytab
	$(MAKE) conda-develop_jupytab-server

samples-kernel:
	ipython kernel install --name jupytab-demo --user

test_jupytab-server:
	pytest ./jupytab-server/tests --junitxml=_build/tests/results.xml

test_jupytab:
	pytest ./jupytab/tests --junitxml=_build/tests/results.xml

test:
	$(MAKE) test_jupytab
	python -m ipykernel install --user --name jupytab-demo
	$(MAKE) test_jupytab-server

flake8_jupytab-server:
	(cd jupytab-server && flake8)

flake8_jupytab:
	(cd jupytab && flake8)

flake8:
	$(MAKE) flake8_jupytab
	$(MAKE) flake8_jupytab-server

demo:
	python -m ipykernel install --user --name jupytab-demo
	python -m jupytab --config ./tests/data/config.ini
