"""The processor of pygohome."""

import datetime as dt
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import utm


class ProcessError(Exception):
    """Process Error."""

    pass


class RegionTooLargeError(ProcessError):
    """Region too large."""

    pass


class EmptyDataError(ProcessError):
    """Empty data error."""

    pass


def prepare_tracks(trackpoints: List[Tuple[dt.datetime, float, float]]) -> Dict:
    """Prepare the trackpoints to DataFrame."""
    # create 3 Series sorted by timestamp
    if not trackpoints:
        raise EmptyDataError("Trackpoints are empty.")
    raw_dfr = pd.DataFrame.from_records(
        trackpoints, columns=("timestamp", "latitude", "longitude")
    ).sort_values("timestamp")
    timestamp = raw_dfr["timestamp"]
    latitude = raw_dfr["latitude"]
    longitude = raw_dfr["longitude"]

    # convert lat/lon to UTM
    utm_x, utm_y, utm_zone, utm_ch = latlon_to_utm(latitude, longitude)

    # split into numbered segments (at least 1 minute break between points)
    segment = (timestamp.diff() > pd.Timedelta("00:01:00")).cumsum()

    # calculate offset to the first record of each segment in seconds
    offset = (
        (timestamp - timestamp.groupby(segment).transform("first"))
        .dt.total_seconds()
        .astype(int)
    )

    dfr = pd.DataFrame(
        {
            "segment": segment,  # same integer for all rows of the same segment
            "offset": offset,  # offset in seconds since the first entry in segment
            "utm_x": utm_x,  # utm easting
            "utm_y": utm_y,  # utm northing
        }
    )
    return {"dfr": dfr, "utm_zone": utm_zone, "utm_ch": utm_ch}


def prepare_waypoints(waypoints: List[Tuple[str, float, float]]) -> Dict:
    """Prepare the waypoints to DataFrame."""
    # create 3 Series sorted by timestamp
    if not waypoints:
        raise EmptyDataError("Waypoints are empty.")
    raw_dfr = pd.DataFrame.from_records(
        waypoints, columns=("name", "latitude", "longitude")
    ).set_index("name")
    latitude = raw_dfr["latitude"]
    longitude = raw_dfr["longitude"]
    utm_x, utm_y, utm_zone, utm_ch = latlon_to_utm(latitude, longitude)

    dfr = pd.DataFrame({"utm_x": utm_x, "utm_y": utm_y})
    return {"dfr": dfr, "utm_zone": utm_zone, "utm_ch": utm_ch}


def latlon_to_utm(
    latitude: pd.Series, longitude: pd.Series
) -> Tuple[pd.Series, pd.Series, int, str]:
    """Convert lat/lon to UTM."""
    utm_x, utm_y, utm_zone, utm_ch = utm.from_latlon(latitude.values, longitude.values)
    utm_x = pd.Series(utm_x, index=longitude.index).astype(int)
    utm_y = pd.Series(utm_y, index=longitude.index).astype(int)

    # if the region does not fit into a single UTM zone, raise an exception
    if 400000 < np.abs(utm_x - 500000).max():
        raise RegionTooLargeError(
            f"Region too large, does not fit into a single UTM zone: "
            f"lat {latitude.min():.2f}…{latitude.max():.2f}, "
            f"lon {longitude.min():.2f}…{latitude.max():.2f}."
        )
    return utm_x, utm_y, utm_zone, utm_ch
