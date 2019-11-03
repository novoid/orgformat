# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name="orgformat",
    version="2019.11.03.1",
    description="Utility library for providing functions to generate and modify Org mode syntax elements like links, time-stamps, or date-stamps.",
    license='GPLv3',
    author="Karl Voit",
    author_email="tools@Karl-Voit.at",
    url="https://github.com/novoid/orgformat",
    download_url="https://github.com/novoid/orgformat/zipball/master",
    keywords=["orgmode", "datestamps", "timestamps", "links"],
    packages=find_packages(),
    #install_requires=["pyreadline", "clint"],  # add dependencies if they are included in the code
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        ]
)
