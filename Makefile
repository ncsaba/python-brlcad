install: clean
	python setup.py install

clean:
	rm -fr build/
	rm -fr dist/
	rm -fr ctypesgen-0.0.1-py2.7.egg/
	rm -fr ctypesgen_dev*.egg/
	rm -fr brlcad.egg-info/
	- pip uninstall -y brlcad
	- pip uninstall -y ctypesgen
	- pip uninstall -y ctypesgen-dev
	rm -fr $(VIRTUAL_ENV)/lib/python2.7/site-packages/brlcad-0.0.1-py2.7.egg
	rm -fr $(VIRTUAL_ENV)/lib/python2.7/site-packages/brlcad

sdist: clean
	python setup.py sdist

upload: clean
	python setup.py sdist upload

all: clean install
