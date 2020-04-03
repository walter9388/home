import pandas as pd
import panel as pn
import numpy as np
import param
import os

import altair as alt


css = '''
.widget-box {
  background: #f0f0f0;
  border-radius: 5px;
  border: 1px black solid;
}
'''

pn.extension(raw_css=[css])

try:
    # data=pd.read_csv('data.csv',index_col=(0,1,2,3,4))
    df2=pd.read_csv('data2.csv',header=[0,1,2],index_col=0)
    df3=pd.read_csv('data3.csv',header=[0,1,2],index_col=0)
except:
    # data=pd.read_csv('data.csv',index_col=(0,1,2,3,4))
    df2=pd.read_csv('heroku/solver_comparison/data2.csv',header=[0,1,2],index_col=0)
    df3=pd.read_csv('heroku/solver_comparison/data3.csv',header=[0,1,2],index_col=0)



import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Slider, TextInput
from bokeh.plotting import figure


checkbox1 = pn.widgets.Checkbox(name='Checkbox',value=True)

headloss_button = pn.widgets.RadioButtonGroup(
    value=list(df2.columns.levels[1])[0],
    options=list(df2.columns.levels[1]),
    button_type='default')

dma_button = pn.widgets.RadioButtonGroup(
    value=list(df2.columns.levels[0])[0],
    options=list(df2.columns.levels[0]),
    button_type='default')

grouping_button = pn.widgets.RadioButtonGroup(
    value=list(df2.columns.levels[2])[-1],
    options=list(df2.columns.levels[2])[::-1],
    button_type='default')

@pn.depends(dma_button,headloss_button,grouping_button,checkbox1)
def bokeh_pane(dma,headloss,grouping,checkbox1):

    x = df2[(dma,headloss,grouping)]
    y = np.linspace(0,100,len(x))

    x2 = df3[(dma,headloss,grouping)]
    y2 = np.linspace(0,100,len(x2))


    # Set up plot
    p = figure(title='Randomised Starting Points - CDF: BWFL - {} - {} - {}'.format(dma,headloss,grouping),
               tools="reset,save,xwheel_zoom,xpan,hover",
               active_scroll='xwheel_zoom',
               y_range=(0, 100),
               x_axis_label='Validation Error',
               y_axis_label='% tests',
               )

    # line 1
    if checkbox1:
        p.line(x,y,line_width=3, line_alpha=0.6,color="green",legend_label='L-BFGS-B',name='L-BFGS-B')

    # line 2
    p.line(x2,y2,line_width=3, line_alpha=0.6,color="red",legend_label='SCP',name='SCP')

    # legend
    p.legend.title = 'Solver'
    p.legend.location = 'top_left'

    p.hover.mode='vline'
    p.hover.tooltips=[
        ('Solver', '$name'),
        ('% of tests', '$y'),
        ('ψ(val)','$x'),
    ]
    # HoverTool(
    #     tooltips=[
    #         ('date', '@date{%F}'),
    #         ('close', '$@{adj close}{%0.2f}'),  # use @{ } for field names with spaces
    #         ('volume', '@volume{0.00 a}'),
    #     ],
    #
    #     formatters={
    #         '@date': 'datetime',  # use 'datetime' formatter for '@date' field
    #         '@{adj close}': 'printf',  # use 'printf' formatter for '@{adj close}' field
    #         # use default 'numeral' formatter for other fields
    #     },
    #
    #     # display a tooltip whenever the cursor is vertically in line with a glyph
    #     mode='vline'
    # )


    return pn.pane.Bokeh(p, width_policy='max', height_policy='max')

# Set up widgets
# text = TextInput(title="title", value='my sine wave')
# offset = Slider(title="offset", value=0.0, start=-5.0, end=5.0, step=0.1)
# amplitude = Slider(title="amplitude", value=1.0, start=-5.0, end=5.0, step=0.1)
# phase = Slider(title="phase", value=0.0, start=0.0, end=2*np.pi)
# freq = Slider(title="frequency", value=1.0, start=0.1, end=5.1, step=0.1)


# p.axis.axis_label=None
# p.axis.visible=False
# p.grid.grid_line_color = None


# buttons!!
from bokeh.models import RadioButtonGroup




def Headloss_cb(new):
    print(new)
    y = df2[('DMA1',list(df2.columns.levels[1])[new],'nongrouped')]
    source.data = dict(x=x, y=y)

def DMA_cb(new):
    y = df2[('DMA1',list(df2.columns.levels[1])[new],'nongrouped')]
    source.data = dict(x=x, y=y)

def Grouping_cb(new):
    y = df2[('DMA1',list(df2.columns.levels[1])[new],'nongrouped')]
    source.data = dict(x=x, y=y)








# dd=pn.pane.Bokeh(headloss_button)


# radio_button_group.js_link(p.x,value=df2[('DMA1','DW','nongrouped')])




pane=pn.Row(
    # pn.Column(
    #     pn.widgets.FloatSlider(name='Number', margin=(10, 5, 5, 10)),
    #     pn.widgets.Select(name='Fruit', options=['Apple', 'Orange', 'Pear'], margin=(0, 5, 5, 10)),
    #     pn.widgets.Button(name='Run', margin=(5, 10, 10, 10)),
    # css_classes=['widget-box']),
    pn.Column(
        dma_button,
        headloss_button,
        grouping_button,
        checkbox1,
    ),
    bokeh_pane
)

# pane.show()


# # Dynamic Tabs
# mypanel=pn.Tabs(
#     ('Altair', altair_pane),
#     ('Bokeh', bokeh_pane),
#     ('deck.GL', deck_gl),
#     ('HoloViews', hv_panel),
#     ('Matplotlib', mpl_pane),
#     ('Plotly', plotly_pane),
#     dynamic=True
# )

mypanel=pane
def call_heroku():
    return mypanel