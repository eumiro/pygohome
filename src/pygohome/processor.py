"""The processor of pygohome."""

import datetime as dt
from typing import Dict, List, Tuple

import networkx as nx
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
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


def prepare_trackpoints(trackpoints: List[Tuple[dt.datetime, float, float]]) -> Dict:
    """Prepare the trackpoints to DataFrame."""
    # create 3 Series sorted by timestamp
    if not trackpoints:
        raise EmptyDataError("Trackpoints are empty.")
    raw_dfr = pd.DataFrame.from_records(
        trackpoints, columns=("timestamp", "latitude", "longitude")
    ).sort_values("timestamp")
    timestamp = raw_dfr.pop("timestamp")

    # convert lat/lon to UTM
    dfr = latlon_to_utm(raw_dfr)

    # split into numbered segments (at least 1 minute break between points)
    dfr["segment"] = (timestamp.diff() > pd.Timedelta("00:01:00")).cumsum()

    # calculate offset to the first record of each segment in seconds
    dfr["offset"] = (
        (timestamp - timestamp.groupby(dfr["segment"]).transform("first"))
        .dt.total_seconds()
        .astype(int)
    )

    return dfr


def prepare_waypoints(waypoints: List[Tuple[str, float, float]]) -> Dict:
    """Prepare the waypoints to DataFrame."""
    # create 3 Series sorted by timestamp
    if not waypoints:
        raise EmptyDataError("Waypoints are empty.")
    dfr = pd.DataFrame.from_records(
        waypoints, columns=("name", "latitude", "longitude")
    ).set_index("name")
    return pd.concat([dfr, latlon_to_utm(dfr)], axis=1)


def latlon_to_utm(latlon: pd.DataFrame) -> pd.DataFrame:
    """Convert lat/lon to UTM."""
    utm_x, utm_y, utm_zone, utm_ch = utm.from_latlon(
        latlon["latitude"].values, latlon["longitude"].values
    )
    dfr = pd.DataFrame(
        {
            "utm_x": utm_x.astype(int),
            "utm_y": utm_y.astype(int),
            "utm_zone": utm_zone,
            "utm_ch": utm_ch,
        },
        index=latlon.index,
    )

    # if the region does not fit into a single UTM zone, raise an exception
    if 400000 < np.abs(dfr["utm_x"] - 500000).max():
        raise RegionTooLargeError(
            f"Region too large, does not fit into a single UTM zone: "
            f"lat {latlon['latitude'].min():.2f}…{latlon['latitude'].max():.2f}, "
            f"lon {latlon['longitude'].min():.2f}…{latlon['latitude'].max():.2f}."
        )
    return dfr


def find_encounters(
    dfr_trackpoints: pd.DataFrame, dfr_waypoints: pd.DataFrame, max_dist: int = 30
) -> pd.DataFrame:
    """Find encounters of tracks near waypoints."""
    # Build a KDTree of all nodes and check if trackpoints are closer than 30 meters
    kdtree = cKDTree(dfr_waypoints[["utm_x", "utm_y"]])
    nodes = kdtree.query(
        dfr_trackpoints[["utm_x", "utm_y"]], distance_upper_bound=max_dist
    )[1]
    dfr = pd.DataFrame(
        {
            "segment": dfr_trackpoints["segment"],
            "offset": dfr_trackpoints["offset"],
            "node_iloc": nodes,
        }
    )[nodes < kdtree.n]
    dfr["node"] = dfr_waypoints.index[dfr.node_iloc]

    # for each encounter get the offset of the first and the last point
    dfr_encounters = dfr.groupby(
        (dfr.node != dfr.groupby("segment")["node"].shift(1)).cumsum()
    ).agg(
        segment=("segment", "first"),
        start=("offset", "first"),
        end=("offset", "last"),
        node=("node", "first"),
    )
    return dfr_encounters


def build_graph(
    dfr_encounters: pd.DataFrame, dfr_waypoints: pd.DataFrame
) -> nx.DiGraph:
    """Build a graph with complete information about the route network."""
    # `pred_secs` between leaving `pred_node` and entering `curr_node`
    # `curr_secs` between entering and leaving `curr_node`
    # `succ_secs` between leaving `curr_node` and entering `succ_node`
    dfr_pred = dfr_encounters.groupby("segment").shift(1, fill_value=-1)
    dfr_succ = dfr_encounters.groupby("segment").shift(-1, fill_value=-1)
    dfr = pd.DataFrame(
        {
            "pred_node": dfr_pred["node"],
            "curr_node": dfr_encounters["node"],
            "succ_node": dfr_succ["node"],
            "pred_secs": dfr_encounters["start"] - dfr_pred["end"],
            "curr_secs": dfr_encounters["end"] - dfr_encounters["start"],
            "succ_secs": dfr_succ["start"] - dfr_encounters["end"],
        }
    )

    is_poi = ~dfr.join(dfr_waypoints, on="curr_node")["curr_node"].str.isdigit()

    # an intersection is "slow" (traffic lights)
    # if at least 25% of tracks spend more than 20 seconds within 30 meters of its node
    is_slow = dfr.groupby("curr_node")["curr_secs"].transform(
        lambda x: x.quantile(0.75) > 20
    )

    grp_slow = (
        dfr[~is_poi & is_slow]
        .query("pred_node != -1 and succ_node != -1")
        .groupby(["pred_node", "curr_node", "succ_node"])
    )
    dfr["succ_secs"] += (
        dfr[~is_poi & ~is_slow]["curr_secs"].reindex(dfr.index).fillna(0)
    )
    dfr.loc[~is_poi & ~is_slow, "curr_secs"] = 0

    grp_simple = dfr.query("succ_node != -1").groupby(["curr_node", "succ_node"])

    # build the graph
    graph = nx.DiGraph()
    graph.add_nodes_from(dfr_waypoints.to_dict("index").items())
    graph.add_edges_from(
        (
            ((curr, pred, curr), (curr, curr, succ), {"secs": sorted(grp["curr_secs"])})
            for (pred, curr, succ), grp in grp_slow
        )
    )
    graph.add_edges_from(
        (
            (
                (curr, curr, succ) if (curr, curr, succ) in graph else curr,
                (succ, curr, succ) if (succ, curr, succ) in graph else succ,
                {"secs": sorted(grp["succ_secs"])},
            )
            for (curr, succ), grp in grp_simple
        )
    )
    for node in graph.nodes:
        if isinstance(node, tuple):
            here, src, dst = node
            graph.add_node(node, **graph.nodes[src if here == src else dst])
    return graph
