#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Standard Setuptools Installer
Attribution:
https://github.com/pypa/sampleproject/blob/main/setup.py
Also see:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
"""

# Always prefer setuptools over distutils
import os
import pathlib
from setuptools import setup

NAME = "ghm"
VERSION = "0.1.0"

DESCRIPTION = "Toolchain to migrate from one Github instance to another"

ORG = "insightsengineering"
AUTHOR = "Insights Engineering"
EMAIL = "insightsengineering@example.com"
REPO = "github-migrator"
KEYWORDS = "github, migration, github-enterprise, devops, utilities"
PACKAGE_DATA = {
    f"{NAME}": ["conf/schema.yaml"],
}
ENTRYPOINTS = {
    "console_scripts": [
        f"{NAME}={NAME}.__init__:cli",
    ],
}

# The directory where this file lives
here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
with open(os.path.join(here, "README.md"), "r", encoding="utf-8") as f:
    long_description = f.read()

# Load requirements file so that setuptools can manage dependency installs
with open("requirements.txt") as f:
    required = f.read().splitlines()

with open("requirements-dev.txt") as f:
    required_dev = f.read().splitlines()
    required_dev.pop(0)

# Configure setup
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=f"https://github.com/{ORG}/{REPO}",
    author=AUTHOR,
    author_email=EMAIL,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Github Migration :: Migration Tools",
        "License :: OSI Approved :: GPL v3.0 License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords=KEYWORDS,
    packages=(NAME, f"{NAME}.tests"),
    test_suite=f"{NAME}.tests",
    python_requires=">=3.6, <4",
    install_requires=required,
    tests_require=required_dev,
    include_package_data=True,
    package_data=PACKAGE_DATA,
    entry_points=ENTRYPOINTS,
    project_urls={
        "Bug Reports": f"https://github.com/{ORG}/{REPO}/issues",
    },
)
