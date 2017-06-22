#!./env/bin/python
from __future__ import absolute_import
from setuptools import setup, find_packages


setup(
    name='aws-utils',
    version='0.1',
    author="Thuita Wachira",
    auuthor_email="thuita.wachira@gmail.com",
    url="https://github.com/thuitaw/aws-utils.git",
    keywords="utilities utils aws ",
    description="aws utilities package",
    include_package_data=True,
    packages=find_packages(exclude=("build")),
    license='GPL',
    test_suite="test",
    install_requires=["boto"],

)
