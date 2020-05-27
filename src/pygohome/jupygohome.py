"""Code from Jupyter notebook.

Call:

    from pygohome.jupygohome import gohome
    gohome()
"""

from typing import Any  # pragma: no cover

import ipyleaflet as lf  # pragma: no cover
import ipywidgets as wd  # pragma: no cover
import numpy as np  # pragma: no cover

from pygohome.world import World  # pragma: no cover


def gohome() -> lf.Map:  # pragma: no cover
    """Execute in a Jupyter Notebook cell."""
    world = World()
    m = lf.Map(
        zoom=14,
        center=(49.0, 8.4),
        interpolation="nearest",
        basemap=lf.basemaps.CartoDB.DarkMatter,
    )

    def action_load(change: Any) -> None:
        uploads = sorted(load_list.value.items())
        load_progress.max = len(uploads)
        for item_i, (_, content) in enumerate(uploads, 1):
            if content["content"]:
                world.add_gpx(content["content"].decode("utf-8"))
            load_progress.value = item_i + 1
        world._ensure_graph()
        pois = sorted(
            node
            for node in world.graph.nodes
            if isinstance(node, str) and not node.isdigit()
        )
        route_src.options = pois
        route_dst.options = pois

    load_list = wd.FileUpload(accept=".gpx", multiple=True)
    load_btn = wd.Button(description="Load GPX files")
    load_btn.on_click(action_load)
    load_progress = wd.IntProgress(
        value=0, min=0, max=0, step=1, bar_style="", orientation="horizontal",
    )

    load_box = wd.VBox(children=[load_list, load_btn, load_progress])

    route = lf.AntPath(locations=[])
    m.add_layer(route)

    route_src = wd.Dropdown(options=[], description="Src:")
    route_dst = wd.Dropdown(options=[], description="Dst:")
    route_slider = wd.FloatSlider(
        value=0.8,
        min=0,
        max=1.0,
        step=0.05,
        description="Quantile:",
        continuous_update=False,
        orientation="horizontal",
        readout=True,
        readout_format=".2f",
    )
    route_btn = wd.Button(description="Find route")
    route_result = wd.Text()

    def action_route(change: Any) -> None:
        fp = world.fastest_path(
            route_src.value, route_dst.value, quantile=route_slider.value
        )
        nodes = world.graph.nodes
        route.locations = [
            (nodes[node]["latitude"], nodes[node]["longitude"]) for node in fp.nodes
        ]
        m.center = (
            nodes[route_src.value]["latitude"],
            nodes[route_src.value]["longitude"],
        )
        period_exp, period_min, period_max = 0, 0, 0
        for edge in fp.edges:
            secs = world.graph.edges[edge]["secs"]
            period_exp += np.quantile(secs, route_slider.value)
            period_min += min(secs)
            period_max += max(secs)

        route_result.value = "{}:{:02d} (min: {}:{:02d}, max: {}:{:02d})".format(
            *divmod(int(period_exp), 60),
            *divmod(int(period_min), 60),
            *divmod(int(period_max), 60)
        )

    route_btn.on_click(action_route)
    route_box = wd.VBox(
        children=[route_src, route_dst, route_slider, route_btn, route_result]
    )

    tab_box = wd.Tab(children=[load_box, route_box])
    tab_box.set_title(0, "Load GPX files")
    tab_box.set_title(1, "Fastest route")

    ctrl_tab = lf.WidgetControl(widget=tab_box, position="topright")
    m.add_control(ctrl_tab)
    m.add_control(lf.FullScreenControl())

    return m
