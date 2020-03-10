import plotly.graph_objects as go
# import chart_studio.plotly as py
import plotly.io as pio
from copy import copy
import numpy as np

from plotting_stuff import qtwidge

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output



np.random.seed(1)

pio.renderers.default = "browser"

n = 10

x = np.arange(0, n)
y1 = np.random.rand(n)
y2 = np.random.rand(n)
y3 = np.random.rand(n)
y4 = np.random.rand(n)
y5 = np.random.rand(n)
y6 = np.random.rand(n)
y7 = np.random.rand(n)

names = ['Set 1', 'Set 2', 'Set 3']

colours = ['crimson', 'darkturquoise', 'lime']

f = go.FigureWidget([go.Scatter(x=x, y=y1, name=names[0]),
                     go.Scatter(x=x, y=y2, name=names[0]),
                     go.Scatter(x=x, y=y3, name=names[1]),
                     go.Scatter(x=x, y=y4, name=names[1]),
                     go.Scatter(x=x, y=y5, name=names[2]),
                     go.Scatter(x=x, y=y6, name=names[2]),
                     go.Scatter(x=x, y=y7, name=names[2]),
                     ])

uniquecol = {}
ii = 0
# change info for hover tings 
for i in range(len(f.data)):
    f.data[i].mode = 'lines'
    f.data[i].hoverlabel.namelength = 0
    f.data[i].text = [f.data[i].name for j in range(n)]
    f.data[i].hovertemplate = '<b>%{text}</b>:' + '<br>X: %{x}' + '<br>Y: %{y:.2f}</br>'
    if f.data[i].name not in uniquecol:
        uniquecol[f.data[i].name] = ii
        ii += 1
        f.data[i].showlegend = True
    else:
        f.data[i].showlegend = False
    f.data[i].line = dict(color=colours[uniquecol[f.data[i].name]])
    f.data[i].opacity = 1
    f.data[i].line.width = 2

f.layout.hovermode = 'closest'
f.layout.title = 'Demo Line Highlighting Plot'
f.layout.xaxis.title = 'X'
f.layout.yaxis.title = 'Y'

# save initial f as f0 to find initial colours and line sizes
f0 = copy(f)


def callbackfunctions(f, j):
    temp = [f.data[i].name == f.data[j].name for i in range(len(f.data))]

    # create our callback function for hover
    def update_point1(trace, points, selector):
        if points.point_inds:
            #         c = '#bae2be'
            s = f0.data[j].line.width * 1.5
            with f.batch_update():
                for i in np.where(temp)[0]:
                    f.data[i].line.width = s
                for i in np.where(~np.array(temp))[0]:
                    f.data[i].opacity = 0.2

                    # create our callback function for unhover

    def update_point2(trace, points, selector):
        if points.point_inds:
            #         c = f0.data[2].line.color
            s = f0.data[j].line.width
            with f.batch_update():  #
                for i in np.where(temp)[0]:
                    f.data[i].line.width = s
                for i in np.where(~np.array(temp))[0]:
                    f.data[i].opacity = 1

    f.data[j].on_hover(update_point1)
    f.data[j].on_unhover(update_point2)


for i in range(len(f.data)):
    callbackfunctions(f, i)

# f

app = dash.Dash()
app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),
    html.Div(children='''
            Dash: A web application framework for Python.
        '''),
    dcc.Graph(
        id='example-graph',
        figure={
            'data': f.data,
            'layout': f.layout
        }
    )
])

qtwidge.rundashqt(app)
