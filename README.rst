.. image:: https://mybinder.org/badge_logo.svg
  :target: https://mybinder.org/v2/gh/eumiro/pygohome/master?filepath=notebooks%2Fpygohome.ipynb

.. image:: https://github.com/eumiro/pygohome/workflows/CI/badge.svg
  :target: https://github.com/eumiro/pygohome/actions?query=workflow%3ACI

.. image:: https://img.shields.io/pypi/v/pygohome.svg
  :target: https://pypi.org/project/pygohome/

.. image:: https://img.shields.io/pypi/pyversions/pygohome.svg
  :target: https://pypi.org/project/pygohome/

.. image:: https://img.shields.io/github/license/eumiro/pygohome
  :target: https://github.com/eumiro/pygohome/


pygohome: Python, Let's Go Home. Quickly.
===========================================

**pygohome** is a 100% personal route optimizer in a known environment based on experience.

You walk/ride/drive frequently between known locations (home, work, school, shops, family, friends, …) using different routes, but would like to know *the optimal route*, that should take *you* the least time possible? *pygohome* uses your recorded GPS tracks to build a route network of *your* world with estimation on how long *you* need to get from A to B using the mean of transport of your choice.

How it works
------------

You track all your trips
~~~~~~~~~~~~~~~~~~~~~~~~

A simple GPS track with 1 or 2 seconds interval works well. Just walk/ride/drive as you are used to, stop at lights, don't speed. You may start tracking before you leave and stop it after you arrive.

You identify your points of interest (and crossroads)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*pygohome* does not use any map data, so you'll have to help it. First, you identify all points of interest (home, work, school, shop, family, friends, pub, club, beach, …) and name them.

In the current version, you'll also have to identify all forks and crossroads where your individual GPS tracks cross, split, or join.

You let *pygohome* build your world
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It will build a route network with your nodes (named POIs and identified intersections) and edges (automatically generated lists of timedeltas you needed to get between the nodes).

You can find the fastest route from A to B
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can choose anywhere between “I'm feeling lucky” (i.e. Sunday 7am, sunny) and “I'd like to make sure I get there in time” (i.e. Friday 5pm, blizzard).

