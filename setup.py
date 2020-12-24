"""
pygohome setup.py
"""
import re
from pathlib import Path
from setuptools import setup, find_packages

NAME = "pygohome"
KEYWORDS = ["gps", "navigation", "routing", "bicycle", "walk", "optimal route"]
CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Environment :: Web Environment",
    "Framework :: Jupyter",
    "Intended Audience :: End Users/Desktop",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: BSD License",
    'Operating System :: OS Independent',
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Topic :: Scientific/Engineering :: GIS",
]
INSTALL_REQUIRES = [
    "gpxpy >= 1.4.2",
    "ipyleaflet >= 0.13.3",
    "ipywidgets >= 7.5.1",
    "networkx >= 2.5",
    "notebook >= 6.1.5",
    "numpy >= 1.19.4",
    "pandas >= 1.1.5",
    "scipy >= 1.5.4",
    "utm >= 0.7.0",
]

# --+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----


if __name__ == "__main__":
    HERE = Path(__file__).resolve().parent
    META_FILE = (HERE / 'src' / NAME / '__init__.py').read_text()
    META = dict(
        re.findall(r"^__(\w+)__ = ['\"]([^'\"]*)['\"]", META_FILE, re.M))
    setup(
        name=NAME,
        description=META["description"],
        license=META["license"],
        url=META["url"],
        version=META["version"],
        author=META["author"],
        author_email=META["email"],
        maintainer=META["author"],
        maintainer_email=META["email"],
        keywords=KEYWORDS,
        long_description=Path("README.rst").read_text(),
        long_description_content_type="text/x-rst",
        packages=find_packages(where="src"),
        package_dir={"": "src"},
        zip_safe=False,
        classifiers=CLASSIFIERS,
        install_requires=INSTALL_REQUIRES,
        extras_require={'test': ['pytest']},
        options={},
        include_package_data=True,
    )
