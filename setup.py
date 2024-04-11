#!/usr/bin/env python

import glob

from setuptools import setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

with open("VERSION") as f:
    version = f.read()

data_files = [
    ("etc", glob.glob("etc/*")),
]
scripts = glob.glob("bin/*")

setup(
    name="ska_src_compute_api",
    version=version,
    description="The compute API for SRCNet.",
    url="",
    author="rob barnsley",
    author_email="rob.barnsley@skao.int",
    packages=[
        "ska_src_compute_api.rest",
        "ska_src_compute_api.common",
        "ska_src_compute_api.client",
        "ska_src_compute_api.models",
    ],
    package_dir={"": "src"},
    data_files=data_files,
    scripts=scripts,
    include_package_data=True,
    install_requires=requirements,
    classifiers=[],
)
