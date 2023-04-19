USER_PYTHON_PATH := $(shell python -c "import site; print(site.getusersitepackages())")

install:
	PYTHONPATH=$(USER_PYTHON_PATH):$$PYTHONPATH python3 -m pip install pip --upgrade
	PYTHONPATH=$(USER_PYTHON_PATH):$$PYTHONPATH pip3 install -r requirements.txt
	PYTHONPATH=$(USER_PYTHON_PATH):$$PYTHONPATH python3 setup.py install --user
	tar xJf benchmarks.tar.xz

test:
	PYTHONPATH=$(USER_PYTHON_PATH):$$PYTHONPATH python3 tests/main_test.py

lint:
	autopep8 bin --in-place --recursive --max-line-length 100 --experimental -a -a -a -a -a
	pylint machsmt --exit-zero
