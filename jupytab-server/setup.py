# Copyright (c) Capital Fund Management
# Distributed under the terms of the MIT License.

from setuptools import setup, find_packages

import distutils.cmd
import pathlib


class MakeVersionCommand(distutils.cmd.Command):
    """Prepare the version of jupytab-server"""

    description = "add extra file to make the version"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        version_file = pathlib.Path(__file__).parent.resolve()
        version_file = version_file.parent / 'VERSION'
        version = version_file.resolve().read_text().strip()
        version_py_file = pathlib.Path(__file__).parent / 'jupytab_server' / '__version__.py'
        with version_py_file.open('w') as stream:
            stream.write(f'__version__ = "{version}"\n')


def read_version():
    version = pathlib.Path(__file__).parent.resolve()
    version_master = version.parent / 'VERSION'
    version_master.resolve()
    version_4_release = version / 'jupytab_server' / '__version__.py'
    if version_4_release.exists():
        v = version_4_release.read_text().strip().split('=')[1].strip()
        # Let's remove quotes
        return v[1:len(v) - 1]
    elif version_master.exists():
        return version_master.read_text().strip()
    else:
        raise FileNotFoundError('no version file can be found')


README = """

Jupytab Server allows you to **explore in Tableau data which is generated
dynamically by a Jupyter Notebook**. You can thus create Tableau data
sources in a very flexible way using all the power of Python.
This is achieved by having Tableau access data through a **web
server created by Jupytab**.

Jupytab Server is built on **solid foundations**: Tableau's Web Data
Connector and the Jupyter Kernel Gateway.

Features:

* **Expose multiple pandas dataframes** to Tableau from a Jupyter
  notebook
* Access **several notebooks** from Tableau through a **single
  entry point** (web server)
* Manage your notebooks using a **web interface**
* **Secure access** to your data

The full documentation is available on the project's home page.
"""

# This call to setup() does all the work
setup(
    cmdclass=dict(make_version=MakeVersionCommand),
    name="jupytab-server",
    version=read_version(),
    description="Connect Tableau to your Jupyter Notebook",
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
    python_requires='>=3.6',
    include_package_data=True,
    install_requires=["jupyter_kernel_gateway"],
    project_urls={
        "Bug Tracker": "https://github.com/CFMTech/Jupytab/issues",
        "Documentation": "https://github.com/CFMTech/Jupytab",
        "Source Code": "https://github.com/CFMTech/Jupytab"
    },
    entry_points={
        "console_scripts": [
            "jupytab=jupytab_server.jupytab:main",
        ]
    },
)
