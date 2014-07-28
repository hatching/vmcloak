import distutils.core


distutils.core.setup(
    name='VMCloak',
    version='0.1.0',
    author='Jurriaan Bremer',
    author_email='jurriaanbremer@gmail.com',
    packages=[
        'vmcloak',
        'vmcloak.data',
        'vmcloak.data.bootstrap',
        'vmcloak.data.hwconf',
    ],
    scripts=[
        'bin/vmcloak',
        'bin/vmcloak-deps',
        'bin/vmcloak-gethwconf',
    ],
    url='http://pypi.python.org/pypi/vmcloak/',
    license='docs/LICENSE.txt',
    description='Automated Virtual Machine Generation and Cloaking '
                'for Cuckoo Sandbox.',
    package_data={
        'vmcloak.data': ['*'],
        'vmcloak.data.bootstrap': ['*'],
        'vmcloak.data.hwconf': ['*'],
        'vmcloak.utils': ['*.sh'],
    },
)
