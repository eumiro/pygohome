"""Test the world module."""

import datetime
from pathlib import Path

from pygohome.world import World


def test_no_trackpoints() -> None:
    """Fresh world contains no trackpoints."""
    world = World()
    assert not world._trackpoints
    assert not world._checked


def test_one_trackpoint() -> None:
    """Fresh world with one trackpoint."""
    world = World()
    world.add_trackpoints(
        [(datetime.datetime(2020, 5, 1, 12, 0, 0, 0, datetime.timezone.utc), 49.0, 8.4)]
    )
    assert len(world._trackpoints) == 1
    assert not world._checked


def test_gpx_1pt() -> None:
    """Fresh world with one trackpoint from a GPX file."""
    world = World()
    world.add_gpx(Path("tests/testdata/osmand_1seg_1pt.gpx").read_text())
    assert len(world._trackpoints) == 1
    assert not world._checked


def test_no_waypoints() -> None:
    """Fresh world contains no waypoints."""
    world = World()
    assert not world._waypoints
    assert not world._checked


def test_one_waypoint() -> None:
    """Fresh world with one node."""
    world = World()
    world.add_waypoints([("station", 48.99420, 8.4003)])
    assert len(world._waypoints) == 1
    assert not world._checked


def test_two_waypoints() -> None:
    """Fresh world with two waypoints."""
    world = World()
    world.add_waypoints([("station", 48.99420, 8.4003), ("castle", 49.0134, 8.4044)])
    assert len(world._waypoints) == 2
    assert not world._checked


def test_gpx_2waypoints() -> None:
    """Fresh world with two waypoints from a GPX file."""
    world = World()
    world.add_gpx(Path("tests/testdata/osmand_2waypoints.gpx").read_text())
    assert len(world._trackpoints) == 0
    assert len(world._waypoints) == 2
    assert not world._checked
