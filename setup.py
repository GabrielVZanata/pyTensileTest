from setuptools import setup

with open("README.md", "r") as arq:
    readme = arq.read()

setup(name='tensile-test-data-manipulation',
    version='0.0.1',
    license='MIT License',
    author='Gabriel Valverde Zanata da Silva',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='gabriel.valverde@hotmail.com',
    keywords='shimadzu tensile test',
    description=u'Um pacote para manipulação de dados de teste de tração, criação e correção de diagramas tensão x deformação.',
    packages=['pyTensileTest'],
    install_requires=['matplotlib.pyplot','numpy','pandas','csv'],
    url='https://github.com/GabrielVZanata/pyTensileTest',)