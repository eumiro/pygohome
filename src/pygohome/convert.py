"""Conversion routines to import tracks."""

from typing import List, Tuple

import gpxpy


class InvalidFileError(Exception):
    """Raised if the file cannot be read correctly."""

    pass


def gpx_to_trackpoints(track_xml: str, max_hdop: int = 16) -> List:
    """Convert GPX XML string to a list of trackpoints."""
    trackpoints: List[Tuple] = []
    try:
        gpx = gpxpy.parse(track_xml)
    except gpxpy.gpx.GPXXMLSyntaxException as exc:
        raise InvalidFileError from exc
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                if point.horizontal_dilution <= max_hdop:
                    trackpoints.append((point.time, point.latitude, point.longitude))
    return trackpoints
