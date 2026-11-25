"""Interactive signed-volume figure for Section 8.2."""

from html import escape
from itertools import product

import numpy as np
import plotly.graph_objects as go
from IPython.display import display


def show_handedness():
    """Reflect the third edge of a parallelepiped across its base."""
    figure = go.Figure()
    colors = ["#3d81f6", "orange", "#d81a60"]
    choices = ["Right-handed · det = 6", "Left-handed · det = −6"]
    bases = list(product(range(2), repeat=3))
    triangles = []
    for fixed in range(3):
        free = [i for i in range(3) if i != fixed]
        for side in range(2):
            corners = []
            for a, b in [(0, 0), (1, 0), (1, 1), (0, 1)]:
                bits = [0, 0, 0]
                bits[fixed], bits[free[0]], bits[free[1]] = side, a, b
                corners.append(bases.index(tuple(bits)))
            triangles.extend([(corners[0], corners[1], corners[2]),
                              (corners[0], corners[2], corners[3])])

    for sign in (1, -1):
        vectors = np.array([[3, 0, 0], [0, 2, 0], [0.6, 0.5, sign]])
        vertices = np.array(bases) @ vectors
        x, y, z = vertices.T
        i, j, k = zip(*triangles)
        figure.add_mesh3d(x=x, y=y, z=z, i=i, j=j, k=k, color=colors[0],
                          opacity=0.12, hoverinfo="skip", visible=(sign == 1))

        edges = []
        for corner, bits in enumerate(bases):
            for axis in range(3):
                if bits[axis] == 0:
                    other = list(bits)
                    other[axis] = 1
                    edges.extend([vertices[corner], vertices[bases.index(tuple(other))], [None]*3])
        x, y, z = zip(*edges)
        figure.add_scatter3d(x=x, y=y, z=z, mode="lines", line=dict(color="#627587", width=3),
                             hoverinfo="skip", visible=(sign == 1))
        for vector, name, color in zip(vectors, ["v₁", "v₂", "v₃"], colors):
            x, y, z = vector
            figure.add_scatter3d(x=[0, x], y=[0, y], z=[0, z], mode="lines+markers+text",
                                 text=["", name], textposition="top center",
                                 textfont=dict(size=17, color=color), marker=dict(size=[2, 5], color=color),
                                 line=dict(width=8, color=color), visible=(sign == 1),
                                 hovertemplate=f"{name} = ({x:g}, {y:g}, {z:g})<extra></extra>")
    count = len(figure.data) // 2
    buttons = [dict(label=label, method="update",
                    args=[dict(visible=[index // count == choice for index in range(2*count)])])
               for choice, label in enumerate(choices)]
    axis = dict(showbackground=False, showgrid=False, zeroline=False,
                showticklabels=False, title="")
    figure.update_layout(
        template="plotly_white", paper_bgcolor="white", showlegend=False,
        font=dict(family="Palatino, serif", color="#202124", size=15),
        margin=dict(l=0, r=0, b=0, t=55), height=390,
        scene=dict(xaxis=dict(**axis, range=[-0.4, 4]), yaxis=dict(**axis, range=[-0.5, 3]),
                   zaxis=dict(**axis, range=[-1.35, 1.35]), aspectmode="data",
                   camera=dict(eye=dict(x=1.05, y=-1.55, z=0.9)), uirevision="handedness"),
        updatemenus=[dict(type="buttons", direction="right", buttons=buttons, x=0.5,
                          xanchor="center", y=1.14, yanchor="top", pad=dict(t=0, r=0),
                          font=dict(size=13))])
    html = figure.to_html(include_plotlyjs=True, full_html=True,
                          config=dict(displayModeBar=False, responsive=True, scrollZoom=False))
    display({"text/html": '<iframe title="Reflect the third edge of a parallelepiped" '
             'style="display:block;width:100%;height:412px;border:0" srcdoc="'
             + escape(html, quote=True) + '"></iframe>'}, raw=True)
