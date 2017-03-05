from setuptools import setup

with open('mirobo/version.py') as f: exec(f.read())

setup(
    name='python-mirobo',

    version=__version__,
    description='Python library for interfacing with Xiaomi Vacuum cleaner robot',
    url='https://github.com/rytilahti/python-mirobo',

    author='Teemu Rytilahti',
    author_email='tpr@iki.fi',

    license='GPLv3',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
    ],

    keywords='xiaomi vacuum',

    packages=["mirobo"],

    install_requires=['construct', 'click', 'cryptography', 'pretty_cron'],
    entry_points={
        'console_scripts': [
            'mirobo=mirobo.cli:cli',
        ],
    },
)
