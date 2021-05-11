from setuptools import setup
import setuptools

with open('README.md', 'r', encoding='UTF-8') as f:
    long_desc = f.read()

setup(
    name='filematcher',
    author='Matt Antalek',
    long_description=long_desc,
    description='object to help match and organize files for a machine learning project.',
    package_dir={'':'src'},
    packages=setuptools.find_packages(where='src')
)