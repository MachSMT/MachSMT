install:
	python3 -m pip install pip --upgrade
	pip3 install -r requirements.txt
	sudo python3 setup.py install
	tar xJf benchmarks.tar.xz


test:
	python3 tests/regress/main_test.py

lint:
	autopep8 bin --in-place --recursive --max-line-length 100 --experimental -a -a -a -a -a
	pylint machsmt --exit-zero
