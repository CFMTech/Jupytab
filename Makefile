.PHONY: clean clean_py test develop conda-develop flake8 demo

BUILD=_build

clean:
	python setup.py clean

clean_pyc:
	find . -name *.py -exec rm {}\;

develop:
	pip install -r requirements-dev.txt
	pip install -r requirements.txt
	pip install -e . --no-deps

conda-develop:
	conda install -y --file requirements-dev.txt
	conda install -y --file requirements.txt
	python setup.py develop --no-deps

samples-kernel:
	ipython kernel install --name jupytab-demo --user

test:
	pytest ./tests --junitxml=_build/tests/results.xml

flake8:
	flake8 .

demo:
	python -m ipykernel install --user --name jupytab-demo
	python -m jupytab --config ./tests/data/config.ini
