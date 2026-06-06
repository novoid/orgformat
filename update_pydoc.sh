#!/bin/sh
set -o errexit

# result goes to: orgformat.html
uv run python -m pydoc -w orgformat/orgformat.py
# strip the local absolute path so the generated HTML stays portable:
sed -i "s#$(pwd)/##g" orgformat.html

#end
