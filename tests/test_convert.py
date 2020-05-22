"""Test the convert module."""

import datetime as dt
from pathlib import Path

import pytest

import pygohome.convert as conv


@pytest.mark.parametrize(
    "filename", ["emptyfile", "hello_world.txt", "osmand_invalid.gpx"]
)
def test_gpx_invalid_file_fails(filename: str) -> None:
    """Expect an error when reading non-GPX-XML files."""
    content = (Path("tests/testdata") / filename).read_text()
    with pytest.raises(conv.InvalidFileError):
        conv.extract_gpx(content)


def test_gpx_no_points() -> None:
    """Read a valid GPX file with no trackpoints in it."""
    content = Path("tests/testdata/osmand_nopoints.gpx").read_text()
    trackpoints, waypoints = conv.extract_gpx(content)
    assert trackpoints == []
    assert waypoints == []


def test_gpx_one_point() -> None:
    """Read a valid GPX file with one trackpoint in it."""
    content = Path("tests/testdata/osmand_1seg_1pt.gpx").read_text()
    trackpoints, waypoints = conv.extract_gpx(content)
    assert trackpoints == [
        (dt.datetime(2020, 5, 1, 0, 0, tzinfo=dt.timezone.utc), 49.0, 8.4)
    ]
    assert waypoints == []


def test_gpx_two_points() -> None:
    """Read a valid GPX file with two trackpoints in it."""
    content = Path("tests/testdata/osmand_1seg_2pt.gpx").read_text()
    trackpoints, waypoints = conv.extract_gpx(content)
    assert len(trackpoints) == 2
    assert trackpoints[0][0] == dt.datetime(2020, 5, 1, 0, 0, 0, tzinfo=dt.timezone.utc)
    assert trackpoints[0][1] == pytest.approx(49.0)
    assert trackpoints[0][2] == pytest.approx(8.4)
    assert trackpoints[1][0] == dt.datetime(2020, 5, 1, 0, 0, 1, tzinfo=dt.timezone.utc)
    assert trackpoints[1][1] == pytest.approx(49.01)
    assert trackpoints[1][2] == pytest.approx(8.41)
    assert waypoints == []


def test_gpx_one_bad_hdop() -> None:
    """Read a valid GPX file with two trackpoints (one with bad hdop) in it."""
    content = Path("tests/testdata/osmand_bad_hdop.gpx").read_text()
    trackpoints, waypoints = conv.extract_gpx(content)
    assert trackpoints == [
        (dt.datetime(2020, 5, 1, 0, 0, tzinfo=dt.timezone.utc), 49.0, 8.4),
    ]
    assert waypoints == []
