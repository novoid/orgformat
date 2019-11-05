#!/bin/sh
set -o errexit

# pytest is invoking the unit tests:
PYTHONPATH=. pytest-3 orgformat/orgformat_test.py

# mypy is checking the type annotations:
PYTHONPATH=. mypy orgformat/orgformat.py

#end
