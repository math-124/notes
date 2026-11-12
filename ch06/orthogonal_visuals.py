"""Plotly visuals for Math 124, Chapter 6.2."""
import html
import warnings
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
from IPython.display import HTML, Image, display


def composition_widget():
    doc = Path(__file__).with_name('orthogonal-composition-widget.html').read_text()
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', message='Consider using IPython.display.IFrame instead')
        display(HTML('<iframe title="Composing rotations and reflections" srcdoc="'
                     + html.escape(doc, quote=True)
                     + '" style="width:100%;height:1000px;border:0;display:block;background:white;"></iframe>'))


def drone_frame():
    """Side view of the source's drone orientation, rendered as a static PNG."""
    fig = go.Figure()
    for x, y, name, color, label in [(1, 0, 'North', '#66768c', (1.05, -.09)),
                                    (0, 1, 'Vertical up', '#66768c', (0, 1.12)),
                                    (.8, .6, 'Forward', '#3d81f6', (.91, .67)),
                                    (-.6, .8, 'Body up', 'orange', (-.73, .92))]:
        fig.add_annotation(x=x, y=y, ax=0, ay=0, xref='x', yref='y', axref='x', ayref='y',
                           text='', showarrow=True, arrowhead=3, arrowwidth=3, arrowcolor=color)
        fig.add_annotation(x=label[0], y=label[1], text=name, showarrow=False,
                           font=dict(color=color, size=19))
    t = np.linspace(0, np.arctan2(3, 4), 40)
    fig.add_trace(go.Scatter(x=.33*np.cos(t), y=.33*np.sin(t), mode='lines',
                            line=dict(color='#3d81f6', width=2), hoverinfo='skip'))
    fig.add_annotation(x=.43, y=.14, text='θ', showarrow=False, font=dict(size=23))
    fig.update_layout(template='none', width=760, height=400, showlegend=False,
                      paper_bgcolor='white', plot_bgcolor='white',
                      font=dict(family='Palatino, Palatino Linotype, Georgia, serif', size=17),
                      margin=dict(l=20, r=20, t=20, b=45),
                      xaxis=dict(range=[-1.1, 1.3], visible=False),
                      yaxis=dict(range=[-.15, 1.3], visible=False, scaleanchor='x', scaleratio=1))
    fig.add_annotation(x=.5, y=-.12, xref='paper', yref='paper', showarrow=False,
                       text="Side view: the drone's left direction points into the page.")
    display(Image(fig.to_image(format='png', scale=2), width=760))
