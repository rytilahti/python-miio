import re
from setuptools import setup

with open('miio/version.py') as f:
    exec(f.read())


def readme():
    # we have intersphinx link in our readme, so let's replace them
    # for the long_description to make pypi happy
    reg = re.compile(r':.+?:`(.+?)\s?(<.+?>)?`')
    with open('README.rst') as f:
        return re.sub(reg, r'\1', f.read())


setup(
    name='python-miio',

    version=__version__,
    description='Python library for interfacing with Xiaomi smart appliances',
    long_description=readme(),
    url='https://github.com/rytilahti/python-miio',

    author='Teemu Rytilahti',
    author_email='tpr@iki.fi',

    license='GPLv3',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
    ],

    keywords='xiaomi miio vacuum',

    packages=["miio"],

    include_package_data=True,

    python_requires='>=3.5',

    install_requires=[
        'construct',
        'click',
        'cryptography',
        'pretty_cron',
        'zeroconf',
        'attrs',
        'android_backup',
        'pytz',
        'appdirs',
        'tqdm',
        'netifaces',
    ],

    entry_points={
        'console_scripts': [
            'mirobo=miio.vacuum_cli:cli',
            'miplug=miio.plug_cli:cli',
            'miceil=miio.ceil_cli:cli',
            'mieye=miio.philips_eyecare_cli:cli',
            'miio-extract-tokens=miio.extract_tokens:main',
            'miiocli=miio.cli:create_cli',
        ],
    },
)
