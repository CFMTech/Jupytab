Development Guide
=================


Install environment
-------------------

- `notetab` is provided with a Makefile so as to ease environment setup.
-  Both `pip ` and `conda` environments are supported.

### Setup with pip

From the [notetab package folder](../../notetab):

```bash
$ virtualenv ~/envs/notetab
$ source ~/envs/notetab/activate
(notetab) $ make develop
```

### Setup with conda

From the [notetab package folder](../../notetab):

```bash
$ conda create -n notetab python=3
$ conda activate notetab
(notetab) $ make conda-develop
```

### Run demo

The command `make demo` registers the `notetab-demo` kernel and runs the examples:

```bask
(notetab) $ make demo
python -m ipykernel install --user --name notetab-demo
Installed kernelspec notetab_demo in /home/user/.local/share/jupyter/kernels/notetab-demo
python -m notetab --config ./tests/data/config.ini
Start notebook AirFlights.ipynb on 127.0.0.1:51455
Start notebook RealEstateCrime.ipynb on 127.0.0.1:42963
```

Unit tests 
----------

- Unit tests are provided for the pytest framework.
- Test cases are located in the `tests` folder.
- The `make test` command runs all tests:


```bash
(notetab) [user@localhost notetab]$ make test
pytest ./tests
==================================================== test session starts ============================
platform linux -- Python 3.6.2, pytest-3.2.3, py-1.4.33, pluggy-0.4.0
rootdir: /home/user/contrib/notetab, inifile:
plugins: cov-2.5.1
collected 1 item

tests/test_util.py .

================================================= 1 passed in 0.32 seconds ==========================
```
