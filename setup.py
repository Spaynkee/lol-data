from setuptools import setup, find_packages

setup(
    name="lol_data",
    version="0.1.0",
    packages=find_packages(where="resources/python"),
    package_dir={"": "resources/python"},
    install_requires=[],
)