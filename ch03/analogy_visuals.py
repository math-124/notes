"""Machine diagrams and a line-preservation example for Chapter 3."""
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from chapter3_visuals import style, arrow, BLUE, ORANGE, PINK


def machine():
    fig = style(go.Figure(), height=330)
    fig.update_layout(margin=dict(l=15, r=15, t=25, b=20))
    fig.update_xaxes(visible=False, range=[0, 10])
    fig.update_yaxes(visible=False, range=[0, 4])
    fig.add_shape(type='rect', x0=3.2, x1=6.8, y0=.6, y1=3.3,
                  line=dict(color='#586577', width=2), fillcolor='#f5f7fb')
    def label(x, y, text, color='#202124', size=20):
        fig.add_annotation(x=x, y=y, text=text, showarrow=False,
                           font=dict(color=color, size=size))
    label(1.3, 3.2, 'Input vector', BLUE)
    label(8.7, 3.2, 'Output vector', ORANGE)
    label(1.3, .45, 'Domain ℝ²', BLUE, 17)
    label(8.7, .45, 'Codomain ℝ²', ORANGE, 17)
    label(1.3, 2, r'$\vec v=\begin{bmatrix}3\\-1\end{bmatrix}$')
    label(8.7, 2, r'$T(\vec v)=\begin{bmatrix}2\\3\end{bmatrix}$')
    label(5, 2.85, 'Machine T')
    label(5, 1.9, r'$A=\begin{bmatrix}1&1\\1&0\end{bmatrix}$')
    label(5, 1, 'Multiply by A', size=18)
    arrow(fig, [2.35, 2], [3.1, 2], BLUE)
    arrow(fig, [6.9, 2], [7.65, 2], ORANGE)
    return fig


def lines_stay_lines():
    A = np.array([[1, 1], [1, 0]])
    points = np.array([[0, 1], [1, 1], [2, 1]])
    line = np.array([[-.5, 1], [2.5, 1]])
    fig = style(make_subplots(rows=1, cols=2,
        subplot_titles=['Domain: points on y = 1', 'Output: points on y = x − 1'],
        horizontal_spacing=.15), height=400)
    for col, M in [(1, np.eye(2)), (2, A)]:
        transformed_line = line @ M.T
        fig.add_trace(go.Scatter(x=transformed_line[:, 0], y=transformed_line[:, 1],
            mode='lines', line=dict(color='#9caaba', width=2)), row=1, col=col)
        for p, name, color, symbol in zip(points @ M.T, ['P', 'Q', 'R'],
                                        [BLUE, ORANGE, PINK], ['circle', 'square', 'diamond']):
            label = name if col == 1 else 'T(' + name + ')'
            fig.add_trace(go.Scatter(x=[p[0]], y=[p[1]], mode='markers+text',
                text=[label], textposition='top center',
                marker=dict(color=color, size=13, symbol=symbol)), row=1, col=col)
        fig.update_xaxes(range=[-1, 4], title_text='x', row=1, col=col)
        fig.update_yaxes(range=[-1, 3], title_text='y', scaleanchor='x' if col == 1 else 'x2',
                         scaleratio=1, row=1, col=col)
    return fig
