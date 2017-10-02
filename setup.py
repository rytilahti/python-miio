from setuptools import setup

with open('miio/version.py') as f: exec(f.read())

setup(
    name='python-miio',

    version=__version__,
    description='Python library for interfacing with Xiaomi smart appliances',
    url='https://github.com/rytilahti/python-miio',

    author='Teemu Rytilahti',
    author_email='tpr@iki.fi',

    license='GPLv3',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
    ],

    keywords='xiaomi miio vacuum',

    packages=["miio", "mirobo"],

    install_requires=['construct', 'click', 'cryptography', 'pretty_cron', 'typing', 'zeroconf'],
    entry_points={
        'console_scripts': [
            'mirobo=miio.vacuum_cli:cli',
            'miplug=miio.plug_cli:cli',
            'miceil=miio.ceil_cli:cli',
            'mieye=miio.philips_eyecare_cli:cli',
            'miio-extract-tokens=miio.extract_tokens:main'
        ],
    },
)
