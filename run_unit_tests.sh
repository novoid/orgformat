#!/bin/sh
set -o errexit

# pytest is invoking the unit tests:
PYTHONPATH=. pytest-3 orgformat/orgformat_test.py

# mypy is checking the type annotations:
PYTHONPATH=. mypy orgformat/orgformat.py

# OK, this is not a unit test but this doesn't take long and updated docu is always good:
./update_pydoc.sh

#end
