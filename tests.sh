#!/bin/bash
pep8 --ignore=E226,E402 dependenpy/utils.py &&
pyflakes dependenpy/utils.py || exit 1
pylint -f colorized -d C0103 dependenpy/utils.py || true
