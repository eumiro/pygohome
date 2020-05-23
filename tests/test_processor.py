"""Test the processor module."""

import datetime as dt

import pandas as pd
import pytest

import pygohome.processor as processor


def test_prepare_trackpoints_empty_raises() -> None:
    """Empty list returns an empty DataFrame."""
    with pytest.raises(processor.EmptyDataError):
        processor.prepare_trackpoints([])


def test_prepare_trackpoints_one_row_ok() -> None:
    """One record returns good data."""
    trackpoints = [(dt.datetime(2020, 5, 1, tzinfo=dt.timezone.utc), 49.00, 8.40)]
    result = processor.prepare_trackpoints(trackpoints)
    expected = pd.DataFrame(
        {
            "utm_x": [456114],
            "utm_y": [5427629],
            "utm_zone": [32],
            "utm_ch": ["U"],
            "segment": [0],
            "offset": [0],
        }
    )
    pd.testing.assert_frame_equal(result, expected)


def test_prepare_trackpoints_one_segment_ok() -> None:
    """Two records in same segment is ok."""
    trackpoints = [
        (dt.datetime(2020, 5, 1, 0, 0, 0, 0, dt.timezone.utc), 49.00, 8.40),
        (dt.datetime(2020, 5, 1, 0, 0, 2, 0, dt.timezone.utc), 49.01, 8.41),
    ]
    result = processor.prepare_trackpoints(trackpoints)
    expected = pd.DataFrame(
        {
            "utm_x": [456114, 456854],
            "utm_y": [5427629, 5428735],
            "utm_zone": 32,
            "utm_ch": "U",
            "segment": [0, 0],
            "offset": [0, 2],
        }
    )
    pd.testing.assert_frame_equal(result, expected)


def test_prepare_trackpoints_two_segments_ok() -> None:
    """Two records in two segments is ok."""
    trackpoints = [
        (dt.datetime(2020, 5, 1, 0, 0, 0, 0, dt.timezone.utc), 49.00, 8.40),
        (dt.datetime(2020, 5, 1, 1, 0, 0, 0, dt.timezone.utc), 50.00, 8.40),
    ]
    result = processor.prepare_trackpoints(trackpoints)
    expected = pd.DataFrame(
        {
            "utm_x": [456114, 456999],
            "utm_y": [5427629, 5538803],
            "utm_zone": 32,
            "utm_ch": "U",
            "segment": [0, 1],
            "offset": [0, 0],
        }
    )
    pd.testing.assert_frame_equal(result, expected)


def test_prepare_trackpoints_too_far_away_fails() -> None:
    """Two records too far away is bad."""
    trackpoints = [
        (dt.datetime(2020, 5, 1, 0, 0, 0, 0, dt.timezone.utc), 49.00, 8.40),
        (dt.datetime(2020, 5, 1, 1, 0, 0, 0, dt.timezone.utc), 49.00, -8.40),
    ]
    with pytest.raises(processor.RegionTooLargeError):
        processor.prepare_trackpoints(trackpoints)


def test_prepare_waypoints_empty_raises() -> None:
    """Empty list returns an empty DataFrame."""
    with pytest.raises(processor.EmptyDataError):
        processor.prepare_waypoints([])


def test_prepare_waypoints_two_ok() -> None:
    """Two waypoints are ok."""
    waypoints = [("station", 48.99420, 8.4003), ("castle", 49.0134, 8.4044)]
    result = processor.prepare_waypoints(waypoints)
    expected = pd.DataFrame(
        {
            "utm_x": [456131, 456448],
            "utm_y": [5426984, 5429116],
            "utm_zone": 32,
            "utm_ch": "U",
        },
        index=pd.Index(["station", "castle"], name="name"),
    )
    pd.testing.assert_frame_equal(result, expected)


def test_prepare_waypoints_too_far_away_fails() -> None:
    """Two records too far away is bad."""
    waypoints = [("east", 49.00, 8.40), ("west", 49.00, -8.40)]
    with pytest.raises(processor.RegionTooLargeError):
        processor.prepare_waypoints(waypoints)
