"""Test the processor module."""

import datetime as dt

import pandas as pd
import pytest

import pygohome.processor as processor


def test_prepare_tracks_empty_raises() -> None:
    """Empty list returns an empty DataFrame."""
    with pytest.raises(processor.EmptyDataError):
        processor.prepare_tracks([])


def test_prepare_tracks_one_row_ok() -> None:
    """One record returns good data."""
    trackpoints = [(dt.datetime(2020, 5, 1, tzinfo=dt.timezone.utc), 49.00, 8.40)]
    result = processor.prepare_tracks(trackpoints)
    expected = {
        "dfr": pd.DataFrame(
            {"segment": [0], "offset": [0], "utm_x": [456114], "utm_y": [5427629]}
        ),
        "utm_zone": 32,
        "utm_ch": "U",
    }
    pd.testing.assert_frame_equal(result.pop("dfr"), expected.pop("dfr"))
    assert result == expected


def test_prepare_tracks_one_segment_ok() -> None:
    """Two records in same segment is ok."""
    trackpoints = [
        (dt.datetime(2020, 5, 1, 0, 0, 0, 0, dt.timezone.utc), 49.00, 8.40),
        (dt.datetime(2020, 5, 1, 0, 0, 2, 0, dt.timezone.utc), 49.01, 8.41),
    ]
    result = processor.prepare_tracks(trackpoints)
    expected = {
        "dfr": pd.DataFrame(
            {
                "segment": [0, 0],
                "offset": [0, 2],
                "utm_x": [456114, 456854],
                "utm_y": [5427629, 5428735],
            }
        ),
        "utm_zone": 32,
        "utm_ch": "U",
    }
    pd.testing.assert_frame_equal(result.pop("dfr"), expected.pop("dfr"))
    assert result == expected


def test_prepare_tracks_two_segments_ok() -> None:
    """Two records in two segments is ok."""
    trackpoints = [
        (dt.datetime(2020, 5, 1, 0, 0, 0, 0, dt.timezone.utc), 49.00, 8.40),
        (dt.datetime(2020, 5, 1, 1, 0, 0, 0, dt.timezone.utc), 50.00, 8.40),
    ]
    result = processor.prepare_tracks(trackpoints)
    expected = {
        "dfr": pd.DataFrame(
            {
                "segment": [0, 1],
                "offset": [0, 0],
                "utm_x": [456114, 456999],
                "utm_y": [5427629, 5538803],
            }
        ),
        "utm_zone": 32,
        "utm_ch": "U",
    }
    pd.testing.assert_frame_equal(result.pop("dfr"), expected.pop("dfr"))
    assert result == expected


def test_prepare_tracks_too_far_away_fails() -> None:
    """Two records too far away is bad."""
    trackpoints = [
        (dt.datetime(2020, 5, 1, 0, 0, 0, 0, dt.timezone.utc), 49.00, 8.40),
        (dt.datetime(2020, 5, 1, 1, 0, 0, 0, dt.timezone.utc), 49.00, -8.40),
    ]
    with pytest.raises(processor.RegionTooLargeError):
        processor.prepare_tracks(trackpoints)


def test_prepare_waypoints_empty_raises() -> None:
    """Empty list returns an empty DataFrame."""
    with pytest.raises(processor.EmptyDataError):
        processor.prepare_tracks([])
