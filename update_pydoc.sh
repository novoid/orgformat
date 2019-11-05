#!/bin/sh
set -o errexit

# result goes to: orgformat.html
pydoc3.5 -w orgformat/orgformat.py
sed -i 's#/home/vk/frankie/src/##g' orgformat.html

#end
