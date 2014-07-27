import distutils.core


distutils.core.setup(
    name='VMCloak',
    version='0.1.0',
    author='Jurriaan Bremer',
    author_email='jurriaanbremer@gmail.com',
    packages=['vmcloak', 'vmcloak.lib'],
    scripts=['bin/vmcloak'],
    url='http://pypi.python.org/pypi/VMCloak/',
    license='docs/LICENSE.txt',
    description='Automated Virtual Machine Generation and Cloaking '
                'for Cuckoo Sandbox.',
    long_description=open('README.rst', 'rb').read(),
)
