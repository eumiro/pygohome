[![Tests](https://github.com/eumiro/pygohome/workflows/Tests/badge.svg)](https://github.com/eumiro/pygohome/actions?workflow=Tests)

# pygohome

## Python, Let's Go Home. Quickly.

**pygohome** is a 100% personal route optimizer in a known environment based on experience.

You walk/ride/drive frequently between known locations (home, work, school, shops, family, friends, …) using different routes, but would like to know *the optimal route*, that should take *you* the least time possible? *pygohome* uses your recorded GPS tracks to build a route network of *your* world with estimation on how long *you* need to get from A to B using the mean of transport of your choice.

## How it works

### You track all your trips

A simple GPS track with 1 or 2 seconds interval works well. Just walk/ride/drive as you are used to, stop at lights, don't speed. You may start tracking before you leave and stop it after you arrive.

### You identify your points of interest (and crossroads)

*pygohome* does not use any map data, so you'll have to help it. First, you identify all points of interest (home, work, school, shop, family, friends, pub, club, beach, …) and name them.

In the current version, you'll also have to identify all forks and crossroads where your individual GPS tracks cross, split, or join.

### You let *pygohome* build your world

It will build a route network with your nodes (named POIs and identified intersections) and edges (automatically generated lists of timedeltas you needed to get between the nodes).

### You can find the fastest route from A to B

You can choose anywhere between “I'm feeling lucky” (i.e. Sunday 7am, sunny) and “I'd like to make sure I get there in time” (i.e. Friday 5pm, blizzard).

## Development Quickstart

The development infrastructure of *pygohome* was heavily inspired by [Hypermodern Python](https://cjolowicz.github.io/posts/hypermodern-python-01-setup/) by Claudio Jolowicz. It uses [nox](https://nox.thea.codes/en/stable/) for test automation and [poetry](https://python-poetry.org/) for dependency management and package creation. To contribute, clone this repository and create a virtual environment containing the necessary tools:

    $ python -m venv pygohome              # create a venv at ./pygohome
    $ pygohome/bin/pip install nox poetry  # install the development dependencies
    $ pygohome/bin/nox                     # run all the tests and checks

To list all nox sessions:

    $ nox -l
    * tests-3.8 -> Run the test suite.
    * tests-3.7 -> Run the test suite.
    * lint-3.8 -> Lint using flake8.
    * lint-3.7 -> Lint using flake8.
    - black -> Run black code formatter.
    * safety -> Scan dependencies for insecure packages.
    * mypy-3.8 -> Type-check using mypy.
    * mypy-3.7 -> Type-check using mypy.

To run only the test suite in Python 3.8, run

    $ nox -s tests-3.8
    
If you want to run tests directly you can use the virtual environments that nox creates directly - they are all located in `.nox`. E.g. if you want to just run one test directly in the Python3.8 test environment you can run:

```text
$ .nox/tests-3-8/bin/pytest -k test_there_is_world

============================== test session starts ==============================
platform linux -- Python 3.8.2, pytest-5.4.2, py-1.8.1, pluggy-0.13.1
rootdir: [...]/pygohome
plugins: cov-2.8.1, mock-3.1.0
collected 2 items / 1 deselected / 1 selected

tests/test_world.py .                                                      [100%]
======================== 1 passed, 1 deselected in 0.02s ========================
```
