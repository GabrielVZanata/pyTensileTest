from setuptools import setup

with open("README.md", "r") as arq:
    readme = arq.read()

setup(name='pyTensileTest',
    version='0.0.3',
    license='MIT License',
    author='Gabriel Valverde Zanata da Silva',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='gabriel.valverde@hotmail.com',
    keywords='shimadzu tensile test',
    description=u'A package for manipulating tensile test data, creating and correcting stress-strain diagrams.',
    packages=['pyTensileTest'],
    install_requires=['matplotlib.pyplot','numpy','pandas','csv'],
    url='https://github.com/GabrielVZanata/pyTensileTest',)