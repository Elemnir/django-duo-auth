import os
import re

from setuptools import find_packages, setup

NAME = 'django-duo-auth'
PACKAGES = find_packages(where='src')
META_PATH = os.path.join("src", "duo_auth", "__init__.py")
CLASSIFIERS = [
    "Environment :: Web Environment",
    "Framework :: Django",
    "Framework :: Django :: 2.2",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: BSD License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Topic :: Internet :: WWW/HTTP",
    "Topic :: Internet :: WWW/HTTP :: Dynamic Content"
]
INSTALL_REQUIRES = ['duo-web']

HERE = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    with open(os.path.join(HERE, *parts), "r") as f:
        return f.read()

META_FILE = read(META_PATH)

def find_meta(tag):
    meta_match = re.search(
        r"^__{meta}__\s*=\s*['\"]([^'\"]*)['\"]".format(meta=tag),
        META_FILE, re.M
    )
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError("Unable to find __{meta}__ string.".format(meta=tag))


setup(
    name=NAME,
    description=find_meta("description"),
    license=find_meta("license"),
    url=find_meta("uri"),
    version=find_meta("version"),
    author=find_meta("author"),
    author_email=find_meta("email"),
    maintainer=find_meta("author"),
    maintainer_email=find_meta("email"),
    long_description=read("README.rst"),
    packages=PACKAGES,
    package_dir={'':'src'},
    include_package_data=True,
    classifiers=CLASSIFIERS,
    install_requires=INSTALL_REQUIRES,
)
