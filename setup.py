from setuptools import setup

setup(
    name='gitapy',
    version='1.0',
    packages=['gitapy'],
    entry_points={
        'console_scripts': [
            'gitapy=gitapy.gitapy:main',
        ],
    },
)
