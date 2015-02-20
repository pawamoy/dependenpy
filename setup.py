#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from distutils.core import setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='dependenpy',
    version='v0.2-beta',
    packages=['dependenpy'],
    license='MPL 2.0',
    
    author='Timothée Mazzucotelli',
    author_email='timothee.mazzucotelli@gmail.com',
    url='https://github.com/Pawamoy/dependenpy',
    download_url = 'https://github.com/Pawamoy/dependenpy/tarball/v0.2-beta',
    
    keywords="dependency matrix dsm",
    description="A Python module that builds a Dependency Matrix for your project.",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
        "Programming Language :: Python",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
    ]
)
