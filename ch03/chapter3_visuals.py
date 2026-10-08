"""Reproducible Plotly illustrations for the Chapter 3 draft notebooks."""
from pathlib import Path
import base64
import html
import warnings
import contextlib
import io
import json
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
from IPython.display import HTML, display

ROOT = Path(__file__).resolve().parents[1]
BLUE, ORANGE, PINK = '#3d81f6', 'orange', '#d81a60'
FONT = "Palatino, 'Palatino Linotype', serif"
if hasattr(pio.defaults, 'headers'):
    pio.defaults.headers = {}


def style(fig, height=420):
    fig.update_layout(template='none', width=780, height=height,
        paper_bgcolor='white', plot_bgcolor='white', font=dict(family=FONT, size=17, color='#202124'),
        margin=dict(l=45,r=25,t=70,b=45), showlegend=False)
    fig.update_xaxes(zeroline=True, zerolinecolor='#9caaba', gridcolor='#edf0f5', dtick=1)
    fig.update_yaxes(zeroline=True, zerolinecolor='#9caaba', gridcolor='#edf0f5', dtick=1)
    return fig


def arrow(fig, start, end, color, label='', col=None, dash='solid'):
    kw=dict(row=1,col=col) if col else {}
    fig.add_trace(go.Scatter(x=[start[0],end[0]],y=[start[1],end[1]],mode='lines',line=dict(color=color,width=3,dash=dash),hoverinfo='skip'),**kw)
    suffix='' if col in (None,1) else str(col)
    fig.add_annotation(x=end[0],y=end[1],ax=start[0],ay=start[1],xref='x'+suffix,yref='y'+suffix,axref='x'+suffix,ayref='y'+suffix,text='',showarrow=True,arrowhead=3,arrowwidth=2,arrowcolor=color)
    if label:fig.add_annotation(x=end[0],y=end[1],xref='x'+suffix,yref='y'+suffix,text=label,showarrow=False,xshift=12,yshift=17,bgcolor='white',font=dict(size=16,color='#202124'))


def polygon(fig, pts, color=BLUE, col=None, dash='solid'):
    pts=np.array(pts);pts=np.vstack([pts,pts[0]])
    fig.add_trace(go.Scatter(x=pts[:,0],y=pts[:,1],mode='lines',fill='toself',fillcolor='rgba(61,129,246,.12)',line=dict(color=color,width=2,dash=dash),hoverinfo='skip'),**(dict(row=1,col=col) if col else {}))


def save_figure(fig, name, alt, caption):
    """Store a crisp PNG and accessible notebook output from the same bytes."""
    # Keep renderer shutdown chatter out of student-facing notebook output.
    with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
        data=fig.to_image(format='png',scale=2)
    folder=ROOT/'ch03/visuals';folder.mkdir(exist_ok=True)
    (folder/(name+'.png')).write_bytes(data)
    encoded=base64.b64encode(data).decode('ascii')
    display(HTML('<figure style="margin:16px 0"><img style="width:100%;height:auto" alt="'+html.escape(alt,quote=True)+'" src="data:image/png;base64,'+encoded+'"><figcaption style="font:16px/1.4 '+FONT+';margin-top:8px">'+html.escape(caption)+'</figcaption></figure>'))


def iframe(document, title, height=720):
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', message='Consider using IPython.display.IFrame instead')
        display(HTML('<iframe title="'+html.escape(title,quote=True)+'" style="display:block;width:100%;height:'+str(height)+'px;border:1px solid #cbd5e1;border-radius:6px;background:white" srcdoc="'+html.escape(document,quote=True)+'"></iframe>'))


def widget(name,title):
    document=(ROOT/'ch03'/name).read_text()
    library=(ROOT/'ch03/vendor/plotly-basic-3.1.0.min.js').read_text()
    iframe(document.replace('/* PLOTLY_BUNDLE */',library.replace('</script','<\\/script')),title)


def input_output():
    fig=style(go.Figure(),height=280)
    fig.update_xaxes(visible=False,range=[0,10]);fig.update_yaxes(visible=False,range=[0,3])
    for x0,x1,color in [(0,2.7,BLUE),(3.6,6.4,'#586577'),(7.3,10,ORANGE)]:
        fig.add_shape(type='rect',x0=x0,x1=x1,y0=.4,y1=2.5,line=dict(color=color,width=2),fillcolor='white')
    for x,text in [(1.35,'<b>Input space ℝ²</b><br><br>Two actuator commands<br>s = 2, t = −1'),(5,'<b>Linear rule</b><br><br>F(s,t) = s u + t v<br>Matrix shape: 3 × 2'),(8.65,'<b>Output space ℝ³</b><br><br>One force in space<br>x = 5, y = 2, z = −3')]:
        fig.add_annotation(x=x,y=1.5,text=text,showarrow=False,font=dict(size=17))
    for a,b in [(2.75,3.5),(6.5,7.2)]:arrow(fig,[a,1.5],[b,1.5],'#586577')
    return fig


def linearity():
    fig=style(make_subplots(rows=1,cols=2,subplot_titles=['Add in the input space','Add in the output space'],horizontal_spacing=.16))
    u=np.array([1,0]);v=np.array([0,1]);A=np.array([[1,1],[0,1]])
    for col,M in [(1,np.eye(2)),(2,A)]:
        a,b=M@u,M@v
        polygon(fig,[[0,0],a,a+b,b],col=col)
        arrow(fig,[0,0],a,BLUE,col=col)
        arrow(fig,a,a+b,ORANGE,col=col,dash='dash')
        suffix='' if col==1 else str(col)
        for point,label,dx,dy in [(a/2,'u' if col==1 else 'T(u)',0,-20),(a+b/2,'v' if col==1 else 'T(v)',24,0)]:
            fig.add_annotation(x=point[0],y=point[1],xref='x'+suffix,yref='y'+suffix,text=label,showarrow=False,xshift=dx,yshift=dy,bgcolor='white',font=dict(size=16))
        arrow(fig,[0,0],a+b,PINK,'u + v' if col==1 else 'T(u + v)',col,dash='dot')
        fig.update_xaxes(range=[-.5,2.7],row=1,col=col)
        fig.update_yaxes(range=[-.5,2],scaleanchor='x'+('' if col==1 else str(col)),row=1,col=col)
    return fig


def linear_affine():
    fig=style(make_subplots(rows=1,cols=2,subplot_titles=['Linear: shear through the origin','Affine: translate the square'],horizontal_spacing=.16))
    square=np.array([[0,0],[1,0],[1,1],[0,1]]);A=np.array([[1,1],[0,1]])
    for col,b in [(1,np.zeros(2)),(2,np.array([2,-1]))]:
        polygon(fig,square@(A.T if col==1 else np.eye(2))+b,col=col)
        fig.add_trace(go.Scatter(x=[0],y=[0],mode='markers',marker=dict(color='#202124',size=8)),row=1,col=col)
        fig.add_trace(go.Scatter(x=[b[0]],y=[b[1]],mode='markers',marker=dict(color=PINK,size=13,symbol='circle-open',line=dict(width=3))),row=1,col=col)
        if col==2:arrow(fig,[0,0],b,PINK,'G(0)',col,dash='dot')
        fig.update_xaxes(range=[-1,5],row=1,col=col)
        fig.update_yaxes(range=[-2,2],scaleanchor='x'+('' if col==1 else str(col)),row=1,col=col)
    return fig


def scene_style(fig):
    fig.update_layout(template='none',paper_bgcolor='white',font=dict(family=FONT,size=15,color='#202124'),margin=dict(l=0,r=0,b=0,t=15),height=470,showlegend=True,legend=dict(orientation='h',y=1.12,font=dict(size=13)),scene=dict(aspectmode='data',xaxis=dict(title='x',backgroundcolor='white',gridcolor='#e1e7ef'),yaxis=dict(title='y',backgroundcolor='white',gridcolor='#e1e7ef'),zaxis=dict(title='z',backgroundcolor='white',gridcolor='#e1e7ef'),camera=dict(eye=dict(x=1.5,y=1.6,z=1))))
    return fig


def vector3(fig,start,end,color,name,dash='solid'):
    start,end=np.array(start),np.array(end)
    fig.add_trace(go.Scatter3d(x=[start[0],end[0]],y=[start[1],end[1]],z=[start[2],end[2]],mode='lines+markers',line=dict(color=color,width=7,dash=dash),marker=dict(size=[0,4],color=color),name=name,hovertemplate=name+'<br>x=%{x}, y=%{y}, z=%{z}<extra></extra>'))


def actuator():
    fig=go.Figure();u=np.array([2,1,0]);v=np.array([-1,0,3])
    s,t=np.meshgrid(np.linspace(-1,2,3),np.linspace(-1,1,3));surface=s[:,:,None]*u+t[:,:,None]*v
    fig.add_trace(go.Surface(x=surface[:,:,0],y=surface[:,:,1],z=surface[:,:,2],colorscale=[[0,'#dce8fb'],[1,'#dce8fb']],opacity=.28,showscale=False,hoverinfo='skip',name='Attainable forces'))
    vector3(fig,[0,0,0],u,BLUE,'Column 1: u')
    vector3(fig,[0,0,0],v,ORANGE,'Column 2: v','dash')
    vector3(fig,[0,0,0],2*u-v,PINK,'Result: 2u − v','dot')
    vector3(fig,2*u,2*u-v,ORANGE,'Add −v','dash')
    scene_style(fig)
    fig.update_layout(scene_camera=dict(eye=dict(x=1.5,y=-1.8,z=1.0)))
    return fig


def line_projection():
    fig=style(go.Figure())
    fig.add_trace(go.Scatter(x=[-1.5,4.5],y=[-2,6],mode='lines',line=dict(color='#9caaba',width=2),hoverinfo='skip'))
    arrow(fig,[0,0],[7,1],BLUE)
    fig.add_annotation(x=3.5,y=.5,text='Input force',showarrow=False,yshift=-23,bgcolor='white',font=dict(size=16))
    arrow(fig,[0,0],[3,4],ORANGE,'Along the rail',dash='dash')
    arrow(fig,[3,4],[7,1],PINK,dash='dot')
    fig.add_annotation(x=5.3,y=2.7,text='Perpendicular remainder',showarrow=False,xshift=20,yshift=20,bgcolor='white',font=dict(size=16))
    w=np.array([.6,.8])*.28;n=np.array([.8,-.6])*.28;p=np.array([3,4])
    q=np.array([p+w,p+w+n,p+n]);fig.add_trace(go.Scatter(x=q[:,0],y=q[:,1],mode='lines',line=dict(color='#586577',width=1.5)))
    fig.update_xaxes(range=[-1,9],title='First force coordinate');fig.update_yaxes(range=[-1,6],scaleanchor='x',title='Second force coordinate')
    return fig


def plane_projection():
    fig=go.Figure();a,z=np.meshgrid(np.linspace(-2,3,3),np.linspace(-1,4,3))
    fig.add_trace(go.Surface(x=a,y=-a,z=z,colorscale=[[0,'#dce8fb'],[1,'#dce8fb']],opacity=.38,showscale=False,hoverinfo='skip'))
    vector3(fig,[0,0,0],[3,1,2],BLUE,'Input')
    vector3(fig,[0,0,0],[1,-1,2],ORANGE,'Projection onto x + y = 0','dash')
    vector3(fig,[1,-1,2],[3,1,2],PINK,'Normal remainder','dot')
    return scene_style(fig)


def rotation_story():
    fig=style(make_subplots(rows=1,cols=2,subplot_titles=['Before the turn','After a 90° counterclockwise turn'],horizontal_spacing=.16))
    shape=np.array([[0,0],[1.7,0],[1.7,.45],[.5,.45],[.5,1.3],[0,1.3]])
    for col,M in [(1,np.eye(2)),(2,np.array([[0,-1],[1,0]]))]:
        polygon(fig,shape@M.T,col=col)
        arrow(fig,[0,0],M@np.array([1,0]),BLUE,'e₁' if col==1 else 'R e₁',col)
        arrow(fig,[0,0],M@np.array([0,1]),ORANGE,'e₂' if col==1 else 'R e₂',col,dash='dash')
        fig.update_xaxes(range=[-2,2.2],row=1,col=col);fig.update_yaxes(range=[-1,2.2],scaleanchor='x'+('' if col==1 else str(col)),row=1,col=col)
    return fig


def shape_flow():
    fig=style(go.Figure(),height=290);fig.update_xaxes(range=[0,10],visible=False);fig.update_yaxes(range=[0,3],visible=False)
    for x,text in [(1.2,'<b>Input in ℝ³</b><br><br>3 coordinates'),(5,'<b>Intermediate in ℝ²</b><br><br>2 coordinates'),(8.8,'<b>Output in ℝ³</b><br><br>3 coordinates')]:
        fig.add_annotation(x=x,y=1.4,text=text,showarrow=False,font=dict(size=17))
    arrow(fig,[2.5,1.4],[3.5,1.4],BLUE);arrow(fig,[6.5,1.4],[7.5,1.4],ORANGE)
    fig.add_annotation(x=3,y=2.2,text='A: 2 × 3',showarrow=False,font=dict(color=BLUE,size=19));fig.add_annotation(x=7,y=2.2,text='B: 3 × 2',showarrow=False,font=dict(color='#805000',size=19))
    fig.add_annotation(x=5,y=.35,text='<b>First A, then B → combined matrix BA has shape 3 × 3</b>',showarrow=False,font=dict(size=18))
    return fig


def shuffle_scale():
    fig=style(make_subplots(rows=1,cols=2,subplot_titles=['Scale first, then shuffle: SD','Shuffle first, then scale: DS'],horizontal_spacing=.15),height=350)
    labels=['First','Second','Third']
    for col,values in [(1,[-14,3,-20]),(2,[35,-18,-4/3])]:
        fig.add_trace(go.Bar(x=labels,y=values,marker_color=[BLUE,ORANGE,PINK],text=['−14','3','−20'] if col==1 else ['35','−18','−4/3'],textposition='outside',cliponaxis=False),row=1,col=col)
        fig.update_yaxes(range=[-25,42],dtick=10,row=1,col=col)
    return fig


def show_3d(fig,title,description):
    # Embed Plotly itself: no CDN or notebook kernel is needed when reading.
    chart=pio.to_html(fig,include_plotlyjs=True,full_html=False,config={'responsive':True,'displaylogo':False,'displayModeBar':False,'modeBarButtonsToRemove':['toImage']})
    camera=json.dumps(fig.layout.scene.camera.to_plotly_json())
    document = ('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>'+html.escape(title)+'</title><style>body{margin:0;background:white;color:#202124;'
        'font:16px/1.4 Palatino,serif}p{margin:12px}.controls{display:flex;flex-wrap:wrap;gap:8px;padding:8px 12px}'
        'button{font:inherit;padding:8px 12px;border:1px solid #586577;background:white;border-radius:4px;'
        'min-height:40px}button:focus-visible{outline:3px solid #3d81f6}</style>'
        '<p><strong>'+html.escape(title)+'</strong><br>'+html.escape(description)+' Use the buttons to rotate with a keyboard.</p>'
        +chart+'<div class="controls"><button id="left">Rotate left</button><button id="right">Rotate right</button>'
        '<button id="above">View from above</button><button id="reset-camera">Reset view</button></div>'
        '<script>const initial='+camera+';let angle=0;const plot=document.querySelector(".js-plotly-plot");'
        'function rotate(delta){angle+=delta;const e=initial.eye,c=Math.cos(angle),s=Math.sin(angle);'
        'Plotly.relayout(plot,{"scene.camera":{eye:{x:c*e.x-s*e.y,y:s*e.x+c*e.y,z:e.z}}});}'
        'document.getElementById("left").onclick=()=>rotate(-Math.PI/8);'
        'document.getElementById("right").onclick=()=>rotate(Math.PI/8);'
        'document.getElementById("above").onclick=()=>Plotly.relayout(plot,{"scene.camera":{eye:{x:0,y:0,z:2.5},up:{x:0,y:1,z:0}}});'
        'document.getElementById("reset-camera").onclick=()=>{angle=0;Plotly.relayout(plot,{"scene.camera":initial});};'
        'new ResizeObserver(()=>{if(window.frameElement)window.frameElement.style.height=Math.ceil(document.body.getBoundingClientRect().height+4)+"px";}).observe(document.body);'
        '</script></html>')
    iframe(document,title,720)
