"""Interactive Plotly figures for Math 124, Chapter 6.1."""
import html
import json
import warnings
from pathlib import Path
import numpy as np
import plotly.graph_objects as go
from IPython.display import HTML, display

COLORS = ['#3d81f6', 'orange', '#d81a60']
PLANE = np.array([[1., 1.], [0., 1.], [1., 2.]])
SPACE = np.array([[1., 2., 3.], [1., 0., 1.], [1., 1., -1.]])


def arrow(v, name, color, origin=None, dashed=False):
    origin = np.zeros(3) if origin is None else np.array(origin)
    v = np.asarray(v, dtype=float)
    tip = origin + v
    size = np.linalg.norm(v)
    if size < 1e-12:
        return []
    shaft = tip - min(.12, size * .18) * v / size
    return [go.Scatter3d(x=[origin[0], shaft[0]], y=[origin[1], shaft[1]],
                        z=[origin[2], shaft[2]], mode='lines', name=name,
                        line=dict(color=color, width=7, dash='dash' if dashed else 'solid'),
                        hovertemplate=name + '<extra></extra>'),
            go.Cone(x=[tip[0]], y=[tip[1]], z=[tip[2]],
                    u=[v[0]/size], v=[v[1]/size], w=[v[2]/size],
                    colorscale=[[0, color], [1, color]], showscale=False,
                    sizemode='absolute', sizeref=.17, anchor='tip',
                    showlegend=False, hoverinfo='skip')]


def label3(point, text, color, size=22):
    return dict(x=float(point[0]), y=float(point[1]), z=float(point[2]),
                text=text, showarrow=False,
                font=dict(family='Palatino', color=color, size=size))


def plane_corners(compact=False):
    u = np.array([1, 0, 1])/np.sqrt(2)
    v = np.array([-1, 2, 1])/np.sqrt(6)
    lo, hi, side = (-1.35, 1.35, 1.25) if compact else (-1.7, 2.9, 1.7)
    return np.array([a*u+b*v for a,b in [(lo,-side),(hi,-side),(hi,side),(lo,side)]])


def plane_traces(compact=False):
    corners = plane_corners(compact)
    boundary = np.vstack((corners, corners[0]))
    return [go.Mesh3d(x=corners[:,0], y=corners[:,1], z=corners[:,2],
                     i=[0,0], j=[1,2], k=[2,3], color=COLORS[0], opacity=.12,
                     hoverinfo='skip', showlegend=False, flatshading=True,
                     lighting=dict(ambient=1, diffuse=0, specular=0)),
            go.Scatter3d(x=boundary[:,0], y=boundary[:,1], z=boundary[:,2],
                         mode='lines', line=dict(color=COLORS[0], width=3),
                         showlegend=False, hoverinfo='skip')]


def plane_label(compact=False):
    return label3(.85*plane_corners(compact)[3], '$P$', COLORS[0], 24)


def layout(limit=3.4):
    axis = dict(range=[-limit,limit], backgroundcolor='white', gridcolor='#e6e9ef',
                zerolinecolor='#aab2bf', showbackground=True, tickfont=dict(size=11),
                showspikes=False, dtick=1)
    return dict(paper_bgcolor='white',plot_bgcolor='white',
                font=dict(family='Palatino, Palatino Linotype, Georgia, serif',size=16,color='#24354a'),
                margin=dict(l=18,r=18,t=18,b=35),
                scene=dict(xaxis=dict(axis,title='x'),yaxis=dict(axis,title='y'),
                           zaxis=dict(axis,title='z'),aspectmode='cube',
                           camera=dict(eye=dict(x=-1.4,y=-1.4,z=1.2))),
                legend=dict(orientation='h',x=0,y=1.03),uirevision='keep-camera',
                showlegend=False)


def embed(doc, title, height):
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', message='Consider using IPython.display.IFrame instead')
        display(HTML('<iframe title="'+html.escape(title,quote=True)+'" srcdoc="'
                     +html.escape(doc,quote=True)+'" style="width:100%;height:'+str(height)
                     +'px;border:0;display:block;background:white;"></iframe>'))


def basis_view(orthonormal=False):
    q = np.column_stack(([1,0,1],[-1,2,1]))/np.sqrt([2,6])
    basis = q if orthonormal else PLANE
    fig = go.Figure(plane_traces(orthonormal))
    annotations = [plane_label(orthonormal)]
    for i in range(2):
        symbol = 'u' if orthonormal else 'v'
        fig.add_traces(arrow(basis[:,i],symbol+['₁','₂'][i],COLORS[i]))
        annotations.append(label3(basis[:,i]+np.array([-.12,.08,.17]),
                                  rf'$\vec{{{symbol}}}_{i+1}$', COLORS[i]))
    if orthonormal:
        t=np.linspace(0,2*np.pi,121)
        c=q[:,0,None]*np.cos(t)+q[:,1,None]*np.sin(t)
        fig.add_trace(go.Scatter3d(x=c[0],y=c[1],z=c[2],mode='lines',
                                  line=dict(color='#65758b',width=3,dash='dot'),
                                  name='Unit circle',hoverinfo='skip',showlegend=False))
        right=np.array([.22*q[:,0],.22*(q[:,0]+q[:,1]),.22*q[:,1]])
        fig.add_trace(go.Scatter3d(x=right[:,0],y=right[:,1],z=right[:,2],mode='lines',
                                  line=dict(color='#28374b',width=4),hoverinfo='skip',showlegend=False))
    fig.update_layout(**layout(2.1 if orthonormal else 3.1))
    fig.update_scenes(annotations=annotations)
    fig.add_trace(go.Scatter3d(x=[0],y=[0],z=[0],mode='markers',
                              marker=dict(color='black',size=3),hoverinfo='skip',showlegend=False))
    title = 'An orthonormal basis of P' if orthonormal else 'Two basis vectors on P: x + y − z = 0'
    caption = ('Both arrows end on the unit circle. The corner marks their right angle.'
               if orthonormal else 'Both arrows lie on the plane, but they are not perpendicular.')
    chart=fig.to_html(full_html=False,include_plotlyjs='cdn',include_mathjax='cdn',div_id='basis-plot',
                      default_height='470px',config={'displayModeBar':False,'responsive':True,'scrollZoom':False})
    doc='<!doctype html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>body{margin:0;background:white;color:#24354a;font:17px Palatino,Georgia,serif}h3{font-size:20px;margin:8px 0}p{margin:7px 0}</style></head><body><h3>'+title+'</h3><p>'+caption+' Drag to rotate; pinch to zoom.</p>'+chart+'</body></html>'
    embed(doc,title,555)


def gram_schmidt_states(a):
    """Record each column, each subtraction, and each normalization."""
    states=[]
    q=[]
    r=np.zeros((a.shape[1],a.shape[1]))
    def record(i,phase,residual,description,coefficient=None,projection=None,before=None):
        states.append(dict(i=i+1,phase=phase,residual=residual.tolist(),
                           accepted=[v.tolist() for v in q],description=description,
                           coefficient=coefficient,projection=None if projection is None else projection.tolist(),
                           before=None if before is None else before.tolist(),r=r.tolist()))
    for i in range(a.shape[1]):
        w=a[:,i].copy()
        record(i,'Start with the next vector',w,
               f'Start with v{i+1}. Keep the {i} unit '+('direction already found.' if i==1 else 'directions already found.'))
        for j,u in enumerate(q):
            coefficient=float(a[:,i]@u)
            projection=coefficient*u
            before=w.copy()
            w=w-projection
            r[j,i]=coefficient
            record(i,f'Subtract the component along u{j+1}',w,
                   f'Subtract (v{i+1} · u{j+1})u{j+1}. The remaining vector is perpendicular to u1'+(f', …, u{j+1}.' if j else '.'),
                   coefficient,projection,before)
        length=float(np.linalg.norm(w))
        assert length>1e-12
        r[i,i]=length
        q.append(w/length)
        record(i,'Normalize',w/length,
               f'Divide the remaining vector by its length, {length:.3f}. This gives u{i+1}, a unit vector. '+
               ('The orthonormal basis is complete.' if i==a.shape[1]-1 else 'Now move to the next original vector.'))
    q=np.column_stack(q)
    assert np.allclose(q.T@q,np.eye(a.shape[1])) and np.allclose(q@r,a)
    return states


def stepper(example='plane'):
    is_plane = example == 'plane'
    a = PLANE if is_plane else SPACE
    title = 'Gram-Schmidt process: two vectors' if is_plane else 'Gram-Schmidt process: three vectors'
    step_layout = layout(3.3)
    bounds = [-2.0, 3.1] if is_plane else [-2.5, 3.5]
    for axis in ['xaxis','yaxis','zaxis']:
        step_layout['scene'][axis]['range'] = bounds
    step_layout['scene']['camera'] = dict(eye=(dict(x=-1.3,y=-1.3,z=1.15) if is_plane
                                                     else dict(x=1.4,y=-.4,z=1.2)))
    step_layout['margin'] = dict(l=8,r=8,t=10,b=12)
    payload = dict(example=dict(a=a.T.tolist(),plane=is_plane,states=gram_schmidt_states(a)),
                   plane_label=plane_label(),
                   plane=json.loads(go.Figure(plane_traces()).to_json())['data'],
                   layout=step_layout,colors=COLORS)
    template = Path(__file__).with_name('gram-schmidt-widget.html').read_text()
    doc = template.replace('__PAYLOAD__',json.dumps(payload)).replace('__TITLE__',title)
    embed(doc,title,1080)
