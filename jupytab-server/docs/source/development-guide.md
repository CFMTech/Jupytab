Development Guide
=================


Install environment
-------------------

- `jupytab` is provided with a Makefile so as to ease environment setup.
- `conda` environments are supported for development


### Setup with conda

From the [jupytab package folder](../../jupytab):

```bash
$ conda create -n jupytab python=3
$ conda activate jupytab
(jupytab) $ make conda-develop
```

### Run demo

The command `make demo` registers the `jupytab-demo` kernel and runs the examples:

```bask
(jupytab) $ make demo
python -m ipykernel install --user --name jupytab-demo
Installed kernelspec jupytab_demo in /home/user/.local/share/jupyter/kernels/jupytab-demo
python -m jupytab --config ./tests/data/config.ini
Start notebook AirFlights.ipynb on 127.0.0.1:51455
Start notebook RealEstateCrime.ipynb on 127.0.0.1:42963
```

Unit tests 
----------

- Unit tests are provided for the pytest framework.
- Test cases are located in the `tests` folder.
- The `make test` command runs all tests:


```bash
(jupytab) [user@localhost jupytab]$ make test
pytest ./tests
==================================================== test session starts ============================
platform linux -- Python 3.6.2, pytest-3.2.3, py-1.4.33, pluggy-0.4.0
rootdir: /home/user/contrib/jupytab, inifile:
plugins: cov-2.5.1
collected 1 item

tests/test_util.py .

================================================= 1 passed in 0.32 seconds ==========================
```
