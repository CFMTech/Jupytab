# Copyright (c) Capital Fund Management
# Distributed under the terms of the MIT License.

import os
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), '..', 'VERSION')) as version_file:
    VERSION = version_file.read().strip()

README = """

Jupytab allows you to **explore in Tableau data which is generated
dynamically by a Jupyter Notebook**. You can thus create Tableau data
sources in a very flexible way using all the power of Python.
This is achieved by having Tableau access data through a **web
server created by Jupytab**.

This package is an helper package to split dependencies between
Jupytab server and your notebook. It only requires pandas.

The full documentation is available on the project's home page.
"""

# This call to setup() does all the work
setup(
    name="jupytab",
    version=VERSION,
    description="Jupytab package to be used in notebooks",
    long_description_content_type="text/markdown",
    long_description=README,
    url="https://github.com/CFMTech/Jupytab",
    author="Brian Tribondeau",
    author_email="brian.tribondeau@cfm.fr",
    license="MIT",
    keywords="jupytab jupyter notebook wdc tableau",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(exclude=["*.tests", "*.tests.*"]),
    include_package_data=True,
    install_requires=["pandas"],
    project_urls={
        "Bug Tracker": "https://github.com/CFMTech/Jupytab/issues",
        "Documentation": "https://github.com/CFMTech/Jupytab",
        "Source Code": "https://github.com/CFMTech/Jupytab"
    }
)
