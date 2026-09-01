"""Shared Plotly styling for the Math 124 notes."""

from numbers import Number

import plotly.io as pio


PALETTE = ("#3d81f6", "orange", "#d81a60")
_PALETTE_FILLS = (
    "rgba(61,129,246,0.18)",
    "rgba(255,165,0,0.18)",
    "rgba(216,26,96,0.18)",
)
_NEUTRALS = {
    "black", "white", "gray", "grey", "transparent",
    "#000", "#000000", "#fff", "#ffffff",
}


def _is_numeric_sequence(value):
    if isinstance(value, (str, bytes)) or value is None:
        return False
    try:
        items = list(value)
    except TypeError:
        return False
    return bool(items) and all(isinstance(item, Number) for item in items)


def _is_string_sequence(value):
    if isinstance(value, (str, bytes)) or value is None:
        return False
    try:
        items = list(value)
    except TypeError:
        return False
    return bool(items) and all(isinstance(item, str) for item in items)


def _primary_color(trace):
    line = getattr(trace, "line", None)
    line_color = getattr(line, "color", None)
    if isinstance(line_color, str):
        return line_color

    marker = getattr(trace, "marker", None)
    marker_color = getattr(marker, "color", None)
    if isinstance(marker_color, str):
        return marker_color
    if _is_string_sequence(marker_color):
        return marker_color[0]

    colorscale = getattr(trace, "colorscale", None)
    if colorscale:
        return colorscale[-1][1]
    return None


def _set_trace_color(trace, color):
    trace_type = getattr(trace, "type", "")

    if trace_type in {"surface", "cone", "heatmap", "contour", "volume", "isosurface"}:
        trace.colorscale = [[0, color], [1, color]]
        if hasattr(trace, "showscale") and trace_type not in {"heatmap", "contour"}:
            trace.showscale = False

    if trace_type == "mesh3d" and hasattr(trace, "color"):
        trace.color = color

    line = getattr(trace, "line", None)
    if line is not None and hasattr(line, "color"):
        line.color = color

    marker = getattr(trace, "marker", None)
    if marker is not None and hasattr(marker, "color"):
        marker_color = marker.color
        if _is_numeric_sequence(marker_color):
            marker.colorscale = [[0, PALETTE[0]], [0.5, PALETTE[1]], [1, PALETTE[2]]]
        elif _is_string_sequence(marker_color):
            marker.color = [color] * len(marker_color)
        else:
            marker.color = color

    textfont = getattr(trace, "textfont", None)
    if textfont is not None and getattr(textfont, "color", None):
        textfont.color = color


def style_plotly(fig, renderer="png"):
    """Apply the course palette and choose static or interactive rendering."""
    pio.templates["math124"] = {
        "layout": {
            "paper_bgcolor": "white",
            "plot_bgcolor": "white",
            "font": {"family": "Palatino", "color": "black"},
            "colorway": list(PALETTE),
            "xaxis": {"gridcolor": "#e5e7eb", "zerolinecolor": "#9ca3af"},
            "yaxis": {"gridcolor": "#e5e7eb", "zerolinecolor": "#9ca3af"},
        }
    }
    pio.templates.default = "math124"
    pio.renderers.default = renderer

    fig.update_layout(
        template="math124",
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Palatino", color="black"),
        colorway=list(PALETTE),
    )
    fig.update_xaxes(gridcolor="#e5e7eb", zerolinecolor="#9ca3af")
    fig.update_yaxes(gridcolor="#e5e7eb", zerolinecolor="#9ca3af")
    has_3d = any(
        getattr(trace, "type", "")
        in {"scatter3d", "surface", "cone", "mesh3d", "volume", "isosurface"}
        for trace in fig.data
    )
    if has_3d:
        fig.update_scenes(
            bgcolor="white",
            xaxis_backgroundcolor="white",
            yaxis_backgroundcolor="white",
            zaxis_backgroundcolor="white",
            xaxis_gridcolor="#e5e7eb",
            yaxis_gridcolor="#e5e7eb",
            zaxis_gridcolor="#e5e7eb",
            xaxis_zerolinecolor="#9ca3af",
            yaxis_zerolinecolor="#9ca3af",
            zaxis_zerolinecolor="#9ca3af",
        )

    color_map = {}
    palette_index = 0
    last_color = PALETTE[0]
    previous_type = None

    for trace in fig.data:
        trace_type = getattr(trace, "type", "")
        mode = getattr(trace, "mode", "") or ""
        original = _primary_color(trace)
        normalized = original.lower() if isinstance(original, str) else None

        if mode == "text":
            previous_type = trace_type
            continue

        line = getattr(trace, "line", None)
        dash = getattr(line, "dash", None)
        structural = (
            dash == "dash"
            and normalized in _NEUTRALS
            and getattr(trace, "showlegend", None) is False
        )
        if structural:
            previous_type = trace_type
            continue

        if trace_type == "cone" and previous_type == "scatter3d":
            color = last_color
        elif normalized and normalized not in _NEUTRALS and normalized in color_map:
            color = color_map[normalized]
        else:
            color = PALETTE[palette_index % len(PALETTE)]
            palette_index += 1

        if normalized and normalized not in _NEUTRALS:
            color_map[normalized] = color
        _set_trace_color(trace, color)
        last_color = color
        previous_type = trace_type

    for annotation in fig.layout.annotations or ():
        font_color = getattr(annotation.font, "color", None)
        if isinstance(font_color, str) and font_color.lower() in color_map:
            annotation.font.color = color_map[font_color.lower()]
        arrow_color = getattr(annotation, "arrowcolor", None)
        if isinstance(arrow_color, str) and arrow_color.lower() in color_map:
            annotation.arrowcolor = color_map[arrow_color.lower()]

    shape_index = 0
    for shape in fig.layout.shapes or ():
        fill_color = getattr(shape, "fillcolor", None)
        if fill_color and str(fill_color).lower() not in _NEUTRALS:
            shape.fillcolor = _PALETTE_FILLS[shape_index % len(_PALETTE_FILLS)]
            shape.line.color = PALETTE[shape_index % len(PALETTE)]
            shape_index += 1

    return fig
