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
        conv.gpx_to_trackpoints(content)


def test_gpx_no_points() -> None:
    """Read a valid GPX file with no trackpoints in it."""
    content = Path("tests/testdata/osmand_nopoints.gpx").read_text()
    assert conv.gpx_to_trackpoints(content) == []


def test_gpx_one_point() -> None:
    """Read a valid GPX file with one trackpoint in it."""
    content = Path("tests/testdata/osmand_1seg_1pt.gpx").read_text()
    assert conv.gpx_to_trackpoints(content) == [
        (dt.datetime(2020, 5, 1, 0, 0, tzinfo=dt.timezone.utc), 49.0, 8.4)
    ]


def test_gpx_two_points() -> None:
    """Read a valid GPX file with two trackpoints in it."""
    content = Path("tests/testdata/osmand_1seg_2pt.gpx").read_text()
    result = conv.gpx_to_trackpoints(content)
    assert len(result) == 2
    assert result[0][0] == dt.datetime(2020, 5, 1, 0, 0, 0, tzinfo=dt.timezone.utc)
    assert result[0][1] == pytest.approx(49.0)
    assert result[0][2] == pytest.approx(8.4)
    assert result[1][0] == dt.datetime(2020, 5, 1, 0, 0, 1, tzinfo=dt.timezone.utc)
    assert result[1][1] == pytest.approx(49.01)
    assert result[1][2] == pytest.approx(8.41)


def test_gpx_one_bad_hdop() -> None:
    """Read a valid GPX file with two trackpoints (one with bad hdop) in it."""
    content = Path("tests/testdata/osmand_bad_hdop.gpx").read_text()
    assert conv.gpx_to_trackpoints(content) == [
        (dt.datetime(2020, 5, 1, 0, 0, tzinfo=dt.timezone.utc), 49.0, 8.4),
    ]
