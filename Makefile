DIST = build/ deb_dist/ dist/ VMCloak.egg-info/ \
	   $(wildcard VMCloak-*.tar.gz) MANIFEST

all: pypi deb
	make -C utils/

pypi:
	make -C docs/ html
	python setup.py sdist

deb:
	python setup.py --command-packages=stdeb.command bdist_deb

clean:
	rm -rf $(DIST)
	rm -rf tests/__pycache__
	rm -f $(shell find .|grep .pyc)
	make -C docs/ clean
	make -C utils/ clean
