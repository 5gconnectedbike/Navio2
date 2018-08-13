from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="navio2",
    version="1.0.0",
    author="Ahmet Akgul",
    author_email="ahmet.akgul@ericsson.com",
    license="BSD",
    description="Connected Bike asset tracker",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/5gconnectedbike/Navio2",
    packages=['navio2'],
    install_requires=[
        'smbus==1.1',
        'spidev==3.0'
    ]
)
