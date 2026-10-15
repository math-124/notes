"""Simple Plotly pictures for the revised Chapter 3 drafts."""
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from chapter3_visuals import style, arrow, polygon, scene_style, vector3, BLUE, ORANGE, PINK


def mapping():
    fig=style(go.Figure(),height=450)
    fig.update_layout(margin=dict(l=25,r=25,t=25,b=25))
    fig.update_xaxes(visible=False,range=[-2,8])
    fig.update_yaxes(visible=False,range=[-.9,5.4])
    for center,color,title in [(0,BLUE,'Domain A'),(6,ORANGE,'Codomain B')]:
        fig.add_shape(type='circle',x0=center-1.2,x1=center+1.2,y0=-.6,y1=4.6,
                      line=dict(color=color,width=2),fillcolor='white')
        fig.add_annotation(x=center,y=5,text=title,showarrow=False,font=dict(size=21,color=color))
        for i in range(1,6):
            fig.add_annotation(x=center,y=5-i,text=str(i),showarrow=False,font=dict(size=22))
    for i,j in enumerate([2,4,2,5,4],start=1):
        fig.add_annotation(x=5.65,y=5-j,ax=.35,ay=5-i,xref='x',yref='y',axref='x',ayref='y',
                           text='',showarrow=True,arrowhead=3,arrowwidth=1.7,arrowcolor=BLUE)
    return fig


def transform(matrix, matrix_name="A", matrix_latex=None):
    from fractions import Fraction
    M=np.asarray(matrix)
    def entry(value):
        f = Fraction(float(value)).limit_denominator(1000)
        return str(f.numerator) if f.denominator == 1 else rf'\frac{{{f.numerator}}}{{{f.denominator}}}'
    if matrix_latex is None:
        matrix_latex = r'\begin{bmatrix}' + r'\\'.join('&'.join(entry(v) for v in row) for row in M) + r'\end{bmatrix}'
    fig=style(make_subplots(rows=1,cols=2,subplot_titles=['Before','After'],horizontal_spacing=.14),height=400)
    fig.update_layout(title=dict(text=f'${matrix_name}={matrix_latex}$', x=.5, y=.88, yanchor='middle', font=dict(size=20)), height=470, margin=dict(t=140))
    square=np.array([[0,0],[1,0],[1,1],[0,1]])
    for col,A in [(1,np.eye(2)),(2,M)]:
        transformed=square@A.T
        polygon(fig,transformed,col=col)
        for k,color in [(0,BLUE),(1,ORANGE)]:
            end=A[:,k]
            label=(r'$\vec e_1$' if k==0 else r'$\vec e_2$') if col==1 else (r'$T(\vec e_1)$' if k==0 else r'$T(\vec e_2)$')
            if np.linalg.norm(end)>0:
                arrow(fig,[0,0],end,color,label=label,col=col,label_color=color,label_size=21)
            else:
                fig.add_trace(go.Scatter(x=[0],y=[0],mode='markers',marker=dict(color=color,size=12),hoverinfo='skip'),row=1,col=col)
        x_range=[min(-1.5,transformed[:,0].min()-.7),max(2.5,transformed[:,0].max()+.7)]
        y_range=[min(-1.5,transformed[:,1].min()-.7),max(2.1,transformed[:,1].max()+.7)]
        fig.update_xaxes(range=x_range,dtick=1,row=1,col=col)
        fig.update_yaxes(range=y_range,dtick=1,scaleanchor='x' if col==1 else 'x2',scaleratio=1,row=1,col=col)
    return fig


def projection_line():
    fig=style(go.Figure(),height=420)
    fig.add_trace(go.Scatter(x=[-.5,3.8],y=[-.5,3.8],mode='lines',line=dict(color='#8b95a3',width=2),hoverinfo='skip'))
    arrow(fig,[0,0],[3,1],BLUE,r'$\vec v$',label_color=BLUE,label_size=21)
    arrow(fig,[0,0],[2,2],BLUE,r'$T(\vec v)$',dash='dot',label_color=BLUE,label_size=21)
    fig.add_trace(go.Scatter(x=[3,2],y=[1,2],mode='lines',line=dict(color=PINK,width=2,dash='dot'),hoverinfo='skip'))
    q=np.array([[2.13,2.13],[2.26,2],[2.13,1.87]])
    fig.add_trace(go.Scatter(x=q[:,0],y=q[:,1],mode='lines',line=dict(color='#8b95a3',width=1),hoverinfo='skip'))
    fig.add_annotation(x=3.55,y=3.4,text='y = x',showarrow=False,xanchor='left',xshift=12)
    fig.update_xaxes(range=[-.5,4])
    fig.update_yaxes(range=[-.5,3.8],scaleanchor='x',scaleratio=1)
    return fig


def projection_plane():
    fig=go.Figure()
    x,y=np.meshgrid(np.linspace(-1,3,3),np.linspace(-1,2,3))
    fig.add_trace(go.Surface(x=x,y=y,z=np.zeros_like(x),colorscale=[[0,'#dce8fb'],[1,'#dce8fb']],opacity=.4,showscale=False,hoverinfo='skip',name='xy-plane'))
    vector3(fig,[0,0,0],[2,1,3],BLUE,'v')
    vector3(fig,[0,0,0],[2,1,0],BLUE,'T(v)','dot')
    vector3(fig,[2,1,0],[2,1,3],PINK,'Perpendicular difference','dot')
    return scene_style(fig)
