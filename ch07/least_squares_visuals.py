"""Plotly figures for Math 124, Chapter 7. Run this file to refresh the figures."""
from pathlib import Path
import html
import numpy as np
import plotly.graph_objects as go
from IPython.display import Image, display
from least_squares_projection import projection

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / 'assets'
BLUE, ORANGE, PINK = '#3d81f6', 'orange', '#d81a60'
FONT = 'Palatino, Palatino Linotype, Georgia, serif'
T = np.array([3., 2., 7., 6.])
B = np.array([5., 2., 7., 8.])
A = np.column_stack([np.ones(len(T)), T])
XSTAR = np.linalg.lstsq(A, B, rcond=None)[0]
P = A @ XSTAR


def style(fig, width=1000, height=550):
    fig.update_layout(template='plotly_white', width=width, height=height,
        paper_bgcolor='white', plot_bgcolor='white',
        font=dict(family=FONT, size=20, color='#24354a'),
        margin=dict(l=75, r=30, t=35, b=65),
        legend=dict(orientation='h', x=0, y=1.12, font=dict(size=17)))
    fig.update_xaxes(gridcolor='#e5e8ed', zerolinecolor='#aeb8c6')
    fig.update_yaxes(gridcolor='#e5e8ed', zerolinecolor='#aeb8c6')
    return fig


def small_data(fitted=False, candidates=False, candidate_errors=False):
    fig = go.Figure()
    if candidates:
        xx = np.array([1., 8.])
        for intercept, slope, label, color in [(2, 1, 'y = 2 + t', BLUE), (0, 1, 'y = t', PINK)]:
            fig.add_trace(go.Scatter(x=xx, y=intercept+slope*xx, mode='lines', name=label,
                line=dict(color=color, width=3)))
    if fitted or candidate_errors:
        coeff=np.array([0.,1.]) if candidate_errors else XSTAR
        pred=A@coeff
        xx = np.array([1., 8.])
        fig.add_trace(go.Scatter(x=xx, y=coeff[0]+coeff[1]*xx, mode='lines',
            name='Candidate line: y = t' if candidate_errors else 'Fitted line: y = 1 + t', line=dict(color=BLUE, width=3)))
        for i in range(len(T)):
            fig.add_trace(go.Scatter(x=[T[i], T[i]], y=[pred[i], B[i]], mode='lines',
                name='Vertical error', showlegend=i==0,
                line=dict(color=PINK, width=4, dash='dash')))
        fig.add_trace(go.Scatter(x=T, y=pred, mode='markers', name='Predictions',
            marker=dict(color=BLUE, size=17, symbol='circle-open', line=dict(width=2))))
    fig.add_trace(go.Scatter(x=T, y=B, mode='markers', name='Observations',
        marker=dict(color=ORANGE if fitted or candidates or candidate_errors else BLUE, size=20,
                    line=dict(color='white', width=1.5))))
    style(fig, 800, 700)
    fig.update_layout(showlegend=fitted or candidates or candidate_errors)
    fig.update_xaxes(title='Input, t', range=[1,9], dtick=1, constrain='domain')
    fig.update_yaxes(title='Observed value, y', range=[1,9], dtick=1,
                     scaleanchor='x', scaleratio=1, constrain='domain')
    return fig


def worksheet_scatter():
    """Larger labels and points for the printed Lecture 22 worksheet."""
    fig = small_data()
    fig.update_layout(width=700, height=700, font=dict(size=30),
                      margin=dict(l=110, r=25, t=25, b=110))
    fig.update_xaxes(title=dict(text='Input, t', font=dict(size=30), standoff=16),
                     tickfont=dict(size=27), range=[1,9], dtick=1, gridcolor='#cdd5e0',
                     gridwidth=1, zerolinecolor='#cdd5e0', zerolinewidth=1)
    fig.update_yaxes(title=dict(text='Observed value, y', font=dict(size=30), standoff=18),
                     tickfont=dict(size=27), range=[1,9], dtick=1, gridcolor='#cdd5e0',
                     gridwidth=1, zerolinecolor='#cdd5e0', zerolinewidth=1)
    fig.update_traces(marker=dict(size=23, line=dict(color='white', width=1.5)))
    return fig


def phone_data():
    """Simulated teaching data, not measurements of a real device."""
    data = np.genfromtxt(HERE/'phone-battery.csv', delimiter=',', names=True)
    return data['brightness_percent'], data['streaming_minutes'], data['battery_used_pp']


def phone(fitted=False, controls=False):
    s,t,b=phone_data()
    a=np.column_stack([np.ones(len(s)),s,t])
    xs=np.linalg.lstsq(a,b,rcond=None)[0]
    fig=go.Figure(go.Scatter3d(x=s,y=t,z=b,mode='markers',name='Simulated observations',
        marker=dict(color=BLUE,size=4.5,opacity=.85),
        hovertemplate='Brightness: %{x}%<br>Streaming: %{y} min<br>Battery used: %{z:.1f} pp<extra></extra>'))
    sc=np.array([10,100,100,10]); tc=np.array([0,0,60,60])
    fig.add_trace(go.Mesh3d(x=sc,y=tc,z=xs[0]+xs[1]*sc+xs[2]*tc,
        i=[0,0],j=[1,2],k=[2,3],color=ORANGE,opacity=.42,
        name='Fitted plane',showlegend=True,visible=fitted,hoverinfo='skip',
        lighting=dict(ambient=1,diffuse=0,specular=0)))
    yp=xs@[1,50,30]
    fig.add_trace(go.Scatter3d(x=[50,50],y=[30,30],z=[yp,b[3]],mode='lines+markers',
        name='One vertical error',visible=fitted,
        line=dict(color=PINK,width=8),marker=dict(color=PINK,size=5),
        hovertemplate='Brightness: 50%<br>Streaming: 30 min<br>Battery used: %{z:.2f} pp<extra></extra>'))
    style(fig,1050,650)
    axis=dict(showbackground=True,backgroundcolor='white',gridcolor='#e3e6ec',
              zerolinecolor='#b0bac7',tickfont=dict(size=16))
    fig.update_layout(margin=dict(l=0,r=0,b=0,t=70 if controls else 30),
        legend=dict(x=.02,y=1.02,font=dict(size=17)),
        scene=dict(
            xaxis=dict(**axis,title='Brightness (%)',range=[0,105],dtick=20),
            yaxis=dict(**axis,title='Streaming (minutes)',range=[-3,63],dtick=15),
            zaxis=dict(**axis,title='Battery used (pp)',range=[0,18],dtick=3),
            aspectmode='manual',aspectratio=dict(x=1,y=1,z=.9),
            camera=dict(eye=dict(x=1.5,y=-1.65,z=1.0))),
        uirevision='phone-camera')
    if controls:
        fig.update_layout(updatemenus=[dict(type='buttons',direction='right',x=0,y=1.15,
            xanchor='left',yanchor='top',active=1 if fitted else 0,
            font=dict(family=FONT,size=16),
            buttons=[dict(label='Raw data',method='update',args=[{'visible':[True,False,False]}]),
                     dict(label='Show fitted plane',method='update',args=[{'visible':[True,True,True]}])])])
    return fig


def show_png(name):
    display(Image(filename=str(ASSETS/(name+'.png'))))


def show_projection():
    doc=projection_html()
    display({'text/html':'<iframe title="Rotate the column-space projection" srcdoc="'+html.escape(doc,quote=True)+'" style="width:100%;height:560px;border:0;display:block"></iframe>'},raw=True)


def show_phone():
    display({'text/html':'<iframe title="Phone battery data in three dimensions" srcdoc="'+html.escape(phone_html(),quote=True)+'" style="width:100%;height:560px;border:0;display:block"></iframe>'},raw=True)


def phone_html():
    fig=phone(controls=True)
    fig.update_layout(width=None,height=540,autosize=True)
    return interactive_html(fig,540,"""
let compactPhonePlot;
new ResizeObserver(()=>{
  const compact=host.clientWidth<500;
  if(compact===compactPhonePlot)return;
  compactPhonePlot=compact;
  const changes={
    'height':compact?360:540,
    'scene.camera':{eye:compact?{x:1.8,y:-2,z:1.2}:{x:1.5,y:-1.65,z:1.0}},
    'legend.font.size':compact?11:17,
    'legend.y':compact?1.1:1.02,
    'updatemenus[0].font.size':compact?14:16,
    'updatemenus[0].y':compact?1.22:1.15,
    'margin':compact?{l:0,r:0,t:90,b:0}:{l:0,r:0,t:70,b:0},
    'scene.xaxis.title.text':compact?'s (%)':'Brightness (%)',
    'scene.yaxis.title.text':compact?'t (minutes)':'Streaming (minutes)',
    'scene.zaxis.title.text':compact?'y (pp)':'Battery used (pp)'
  };
  for(const axis of ['xaxis','yaxis','zaxis']){
    changes['scene.'+axis+'.title.font.size']=compact?13:20;
    changes['scene.'+axis+'.tickfont.size']=compact?11:16;
  }
  Plotly.relayout(host,changes);
  try{if(window.frameElement)window.frameElement.style.height=compact?'380px':'560px';}catch(e){}
}).observe(host);
""")


def projection_html():
    fig=projection()
    fig.update_layout(width=None,height=540,autosize=True)
    return interactive_html(fig,540)


def interactive_html(fig,height,extra_script=''):
    return fig.to_html(full_html=True,include_plotlyjs=True,default_width='100%',
        default_height=str(height)+'px',config={'displaylogo':False,'responsive':True},
        post_script="""window.plotReady=true;
const host=document.getElementById('{plot_id}');
new IntersectionObserver(entries=>{
  if(entries.some(e=>e.isIntersecting)){
    Plotly.redraw(host).then(()=>{window.plotVisibleRenders=(window.plotVisibleRenders||0)+1;});
  }
},{threshold:0.01}).observe(host);"""+extra_script)


def render_all():
    ASSETS.mkdir(exist_ok=True)
    figs={'small-data-scatter':small_data(), 'candidate-lines':small_data(candidates=True), 'candidate-errors':small_data(candidate_errors=True),
          'small-data-fit':small_data(fitted=True),'column-space-projection':projection(),
          'phone-raw':phone(),'phone-fit':phone(fitted=True)}
    for name,fig in figs.items():
        fig.write_image(str(ASSETS/(name+'.png')),scale=1.6)
    (ASSETS/'column-space-projection.html').write_text(projection_html())
    (ASSETS/'phone-battery.html').write_text(phone_html())


if __name__=='__main__':
    render_all()


def show_squared_error_explorer():
    """Link the data plot to the squared-error surface for the same line."""
    doc = (HERE / 'least-squares-explorer.html').read_text()
    display({
        'text/html': '<iframe title="Explore the squared error of a line" '
        'style="width:100%;height:440px;border:0;display:block" '
        'srcdoc="' + html.escape(doc, quote=True) + '" '
        'onload="const f=this;const b=f.contentDocument.body;'
        'new ResizeObserver(()=>f.style.height=(b.getBoundingClientRect().height+8)+\'px\').observe(b)">'
        '</iframe>'
    }, raw=True)
