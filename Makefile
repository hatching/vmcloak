DIST = build/ deb_dist/ dist/ $(wildcard VMCloak-*.tar.gz)

pypi:
	make -C docs/ html
	python setup.py sdist

deb:
	python setup.py --command-packages=stdeb.command bdist_deb

clean:
	rm -rf $(DIST)
	make -C docs/ clean
