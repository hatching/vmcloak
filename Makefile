DIST = build/ deb_dist/ dist/ $(wildcard VMCloak-*.tar.gz)

all: pypi deb
	make -C utils/

pypi:
	make -C docs/ html
	python setup.py sdist

deb:
	python setup.py --command-packages=stdeb.command bdist_deb

clean:
	rm -rf $(DIST)
	make -C docs/ clean
	make -C utils/ clean
