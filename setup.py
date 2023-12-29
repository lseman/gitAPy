from setuptools import setup

setup(
    name='gitapy',
    version='0.1',
    packages=['src'],
    entry_points={
        'console_scripts': [
            'gitapy=gitapy.gitapy:main',
        ],
    },
)
