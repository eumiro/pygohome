"""Test the world module."""

import datetime as dt
from pathlib import Path

import pytest

from pygohome.world import RegionTooLargeError, World


def test_no_trackpoints() -> None:
    """Fresh world contains no trackpoints."""
    world = World()
    assert not world.trackpoints
    assert world.graph is None


def test_one_trackpoint() -> None:
    """Fresh world with one trackpoint."""
    world = World()
    world.add_trackpoints(
        [(dt.datetime(2020, 5, 1, 12, 0, 0, 0, dt.timezone.utc), 49.0, 8.4)]
    )
    assert len(world.trackpoints) == 1
    assert world.graph is None


def test_gpx_1pt() -> None:
    """Fresh world with one trackpoint from a GPX file."""
    world = World()
    world.add_gpx(Path("tests/testdata/osmand_1seg_1pt.gpx").read_text())
    assert len(world.trackpoints) == 1
    assert world.graph is None


def test_no_waypoints() -> None:
    """Fresh world contains no waypoints."""
    world = World()
    assert not world.waypoints
    assert world.graph is None


def test_one_waypoint() -> None:
    """Fresh world with one node."""
    world = World()
    world.add_waypoints([("station", 48.99420, 8.4003)])
    assert len(world.waypoints) == 1
    assert world.graph is None


def test_two_waypoints() -> None:
    """Fresh world with two waypoints."""
    world = World()
    world.add_waypoints([("station", 48.99420, 8.4003), ("castle", 49.0134, 8.4044)])
    assert len(world.waypoints) == 2
    assert world.graph is None


def test_gpx_2waypoints() -> None:
    """Fresh world with two waypoints from a GPX file."""
    world = World()
    world.add_gpx(Path("tests/testdata/osmand_2waypoints.gpx").read_text())
    assert len(world.trackpoints) == 0
    assert len(world.waypoints) == 2
    assert world.graph is None


def test_waypoints_far_from_trackpoints() -> None:
    """Waypoints and trackpoints are too far away from each other."""
    world = World()
    world.add_waypoints([("alice", 49.0000, -8.4000), ("bob", 49.0010, -8.4010)])
    world.add_trackpoints(
        [
            (dt.datetime(2020, 5, 1, 0, 0, 0, 0, dt.timezone.utc), 49.0001, 8.4001),
            (dt.datetime(2020, 5, 1, 0, 0, 3, 0, dt.timezone.utc), 49.0005, 8.4005),
            (dt.datetime(2020, 5, 1, 0, 0, 6, 0, dt.timezone.utc), 49.0009, 8.4009),
        ]
    )
    with pytest.raises(RegionTooLargeError):
        world.fastest_path("alice", "bob")


@pytest.fixture
def world1() -> World:
    """Create a simple world with two waypoints."""
    world = World()
    world.add_waypoints([("alice", 49.0000, 8.4000), ("bob", 49.0010, 8.4010)])
    world.add_trackpoints(
        [
            (dt.datetime(2020, 5, 1, 0, 0, 0, 0, dt.timezone.utc), 49.0001, 8.4001),
            (dt.datetime(2020, 5, 1, 0, 0, 3, 0, dt.timezone.utc), 49.0005, 8.4005),
            (dt.datetime(2020, 5, 1, 0, 0, 6, 0, dt.timezone.utc), 49.0009, 8.4009),
        ]
    )
    return world


@pytest.fixture
def world2() -> World:
    """Create a simple world with two waypoints and a slow intersection in between."""
    world = World()
    world.add_waypoints(
        [
            ("alice", 49.00000, 8.40000),
            ("2", 49.00050, 8.40050),
            ("bob", 49.00100, 8.40100),
        ]
    )
    world.add_trackpoints(
        [
            (dt.datetime(2020, 5, 1, 0, 0, 0, 0, dt.timezone.utc), 49.00010, 8.40010),
            (dt.datetime(2020, 5, 1, 0, 0, 3, 0, dt.timezone.utc), 49.00049, 8.40049),
            (dt.datetime(2020, 5, 1, 0, 0, 13, 0, dt.timezone.utc), 49.00050, 8.40050),
            (dt.datetime(2020, 5, 1, 0, 0, 23, 0, dt.timezone.utc), 49.00050, 8.40050),
            (dt.datetime(2020, 5, 1, 0, 0, 33, 0, dt.timezone.utc), 49.00050, 8.40050),
            (dt.datetime(2020, 5, 1, 0, 0, 43, 0, dt.timezone.utc), 49.00050, 8.40050),
            (dt.datetime(2020, 5, 1, 0, 0, 53, 0, dt.timezone.utc), 49.00051, 8.40051),
            (dt.datetime(2020, 5, 1, 0, 0, 56, 0, dt.timezone.utc), 49.00090, 8.40090),
        ]
    )
    return world


def test_fastest_path(world1: World) -> None:
    """Find fastest path between two existing waypoints."""
    result = world1.fastest_path("alice", "bob")
    assert list(result.nodes) == ["alice", "bob"]


def test_fastest_path_with_slow(world2: World) -> None:
    """Find fastest path between two existing waypoints."""
    result = world2.fastest_path("alice", "bob")
    expected = ["alice", ("2", "alice", "2"), ("2", "2", "bob"), "bob"]
    assert list(result.nodes) == expected


def test_graph_rebuilds_one(world1: World) -> None:
    """Graph rebuilds once and once only after each modification."""
    id_graph_0 = id(world1.graph)
    world1.fastest_path("alice", "bob")
    id_graph_1 = id(world1.graph)
    world1.fastest_path("alice", "bob")
    id_graph_2 = id(world1.graph)
    assert id_graph_0 != id_graph_1 == id_graph_2


def test_single_source_periods(world1: World) -> None:
    """Find period to every other waypoint from the src."""
    result = world1.single_source_periods("alice")
    assert result == {"alice": 0, "bob": 6}


def test_single_source_periods_with_slow(world2: World) -> None:
    """Find period to every other waypoint from the src with a slow node."""
    result = world2.single_source_periods("alice")
    assert result == {"alice": 0, "2": 3, "bob": 56}
