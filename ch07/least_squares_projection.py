"""The established EECS 245 column-space diagram, with Math 124 notation.

Provenance: /Users/surajrampure/Desktop/245/notes/
07_regression_using_linear_algebra/01-regression-using-linear-algebra.ipynb,
zero-based cell 8 (repeated in cell 31), stored Plotly output. Its original
generator is plane_style.py:186, projection_figure(..., notation='*').

The companion JSON preserves that figure's geometry, camera, plane, colors,
vector arrows, and right-angle marker. This three-dimensional picture is a
schematic of column-space projection in R^n; it does not represent the
coordinates of the four-observation Math 124 example, whose output vectors
belong to R^4.
"""

import json
from pathlib import Path

import plotly.graph_objects as go


_SOURCE = Path(__file__).with_name("eecs245-projection-base.json")
_LABELS = {
    "<i>y</i>⃗": "<i>b</i>⃗",
    "colsp(<i>X</i>)": "colsp(<i>A</i>)",
    "<i>p</i>⃗ = <i>X</i><i>w</i>⃗<sup>*</sup>":
        "<i>p</i>⃗ = <i>A</i><i>x</i>⃗<sup>*</sup>",
    "<i>e</i>⃗": "<i>r</i>⃗",
}


def projection():
    """Return the established projection figure using A, x*, b, p, and r."""
    fig = go.Figure(json.loads(_SOURCE.read_text(encoding="utf-8")))
    for trace in fig.data:
        if trace.type != "scatter3d" or trace.text is None:
            continue
        old_labels = list(trace.text)
        trace.text = [_LABELS.get(label, label) for label in old_labels]
        if "<i>e</i>⃗" in old_labels:
            # Keep the short error label beside the dashed segment; its
            # definition is given in the surrounding notes.
            trace.textposition = "middle right"
    fig.update_layout(width=1000, height=650, uirevision="math124-eecs245-projection")
    return fig
