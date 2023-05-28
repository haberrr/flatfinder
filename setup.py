from setuptools import setup

setup(
    name='flatfinder',
    version='0.1',
    author='Andrey Pavlov',
    author_email='pavlov.andrey@pm.me',
    install_requires=[
        'mongoengine~=0.25.0',
        'PyYAML~=6.0',
        'requests~=2.28.1',
        'beautifulsoup4~=4.11.1',
        'dacite~=1.8.1',
    ],
    entry_points={
        'console_scripts': [
            'flatfinder=flatfinder.cli:_main',
        ],
    },
)
