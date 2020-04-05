import pandas as pd
import panel as pn
import numpy as np
import param
import os

# import altair as alt

import seaborn as sns

import matplotlib as mpl
from bokeh.plotting import output_file, show

tips = sns.load_dataset("tips")

sns.set_style("whitegrid")




css = '''
.widget-box {
  background: #f0f0f0;
  border-radius: 5px;
  border: 1px black solid;
}
'''

pn.extension('plotly','vega',raw_css=[css])

try:
    # data=pd.read_csv('data.csv',index_col=(0,1,2,3,4))
    df2=pd.read_csv('data2.csv',header=[0,1,2,3],index_col=0)
    df3=pd.read_csv('data3.csv',header=[0,1,2,3],index_col=0)
except:
    # data=pd.read_csv('data.csv',index_col=(0,1,2,3,4))
    df2=pd.read_csv('heroku/solver_comparison/data2.csv',header=[0,1,2,3],index_col=0)
    df3=pd.read_csv('heroku/solver_comparison/data3.csv',header=[0,1,2,3],index_col=0)

solvers=['L-BFGS-B','SCP']

import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Slider, TextInput
from bokeh.plotting import figure


# checkbox1 = pn.widgets.Checkbox(name='L-BFGS-B',value=True)
# checkbox2 = pn.widgets.Checkbox(name='SCP',value=True)
checkbox1 = pn.widgets.CheckBoxGroup(
    name='Checkbox Group', value=['L-BFGS-B', 'SCP'], options=['L-BFGS-B', 'SCP'],
    inline=True)
checkbox2 = pn.widgets.CheckBoxGroup(
    name='Checkbox Group', value=['with reg', 'no reg'], options=['with reg', 'no reg'],
    inline=True)

headloss_button = pn.widgets.RadioButtonGroup(
    value=list(df2.columns.levels[2])[0],
    options=list(df2.columns.levels[2]),
    button_type='default')

dma_button = pn.widgets.RadioButtonGroup(
    value=list(df2.columns.levels[1])[0],
    options=list(df2.columns.levels[1]),
    button_type='default')

grouping_button = pn.widgets.RadioButtonGroup(
    name='asdf',
    value=list(df2.columns.levels[3])[-1],
    options=list(df2.columns.levels[3])[::-1],
    button_type='default')

@pn.depends(dma_button,headloss_button,grouping_button,checkbox1,checkbox2)
def bokeh_pane(dma,headloss,grouping,checkbox1,checkbox2):
    x, y, x_0, y_0 = [0,0], [0,0], [0,0], [0,0]
    for i in range(len(solvers)):
        x[i] = df2[(solvers[i].replace('-',''), dma, headloss, grouping)]
        y[i] = np.linspace(0, 100, len(x[i]))
        x_0[i] = df3[(solvers[i].replace('-',''), dma, headloss, grouping)]
        y_0[i] = np.linspace(0, 100, len(x_0[i]))


    # Set up plot
    p = figure(title='Randomised Starting Points CDF: BWFL - {} - {} - {}'.format(dma,headloss,grouping),
               tools="reset,save,xwheel_zoom,xpan,hover",
               active_scroll='xwheel_zoom',
               y_range=(0, 100),
               x_axis_label='Validation Error',
               y_axis_label='% tests',
               )
    # line 1
    colours=['green','red']
    for i in range(len(solvers)):
        if solvers[i] in checkbox1:
            if 'with reg' in checkbox2:
                p.line(x[i], y[i], line_width=3, line_alpha=0.6, color=colours[i], legend_label=solvers[i], name=solvers[i])
            if 'no reg' in checkbox2:
                p.line(x_0[i], y_0[i], line_width=3, line_alpha=0.6, line_dash='dashed', color=colours[i], legend_label=solvers[i] + ' (no reg)', name=solvers[i] + ' (no reg)')


    # legend
    p.legend.title = 'Solver'
    p.legend.location = 'bottom_right'

    # p.hover.mode='vline'
    p.hover.tooltips=[
        ('Solver', '$name'),
        ('% of tests', '$y'),
        ('ψ(val)','$x'),
    ]

    p.outline_line_color = 'black'

    return pn.pane.Bokeh(p,sizing_mode='stretch_both',width_policy='max')

import plotly.graph_objects as go

@pn.depends(dma_button,headloss_button,grouping_button,checkbox1,checkbox2)
def plotly_violin(dma,headloss,grouping,checkbox1,checkbox2):

    df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/violin_data.csv")

    fig = go.Figure()

    fig.add_trace(go.Violin(x=df['day'][df['smoker'] == 'Yes'],
                            y=df['total_bill'][df['smoker'] == 'Yes'],
                            legendgroup='Yes', scalegroup='Yes', name='Yes',
                            side='negative',
                            line_color='blue')
                  )
    fig.add_trace(go.Violin(x=df['day'][df['smoker'] == 'No'],
                            y=df['total_bill'][df['smoker'] == 'No'],
                            legendgroup='No', scalegroup='No', name='No',
                            side='positive',
                            line_color='orange')
                  )
    fig.update_traces(meanline_visible=True)
    fig.update_layout(violingap=0, violinmode='overlay',margin=dict(l=0, r=0, t=0, b=0))

    return pn.pane.Plotly(fig,sizing_mode='stretch_both',width_policy='max')




# import altair as alt
# from vega_datasets import data
#
# cars = data.cars()
#
# chart = alt.Chart(cars).mark_circle(size=60).encode(
#     x='Horsepower',
#     y='Miles_per_Gallon',
#     color='Origin',
#     tooltip=['Name', 'Origin', 'Horsepower', 'Miles_per_Gallon']
# ).properties(width='container', height='container').interactive()
#
# def tem():
#     return pn.pane.Vega(chart,sizing_mode='stretch_both',width_policy='max')


# plot_buttons=pn.Column(pn.widgets.Button(name='Run', margin=0),
# pn.widgets.Button(name='Run2', margin=0), background='#f0f0f0')


cb_group1 = pn.widgets.CheckButtonGroup(name='Check Button Group', value=['Apple'], options=['Apple', 'Banana'],margin=0)
cb_group2 = pn.widgets.CheckButtonGroup(name='Check Button Group', value=[], options=['Apple', 'Banana'],margin=0)
plot_buttons=pn.Column(
    cb_group1,
    cb_group2
)
# dd=pn.pane.Bokeh(headloss_button)


# radio_button_group.js_link(p.x,value=df2[('DMA1','DW','nongrouped')])

@pn.depends(cb_group1,cb_group2)
def gridspec(cb_group1,cb_group2):
    x=list(cb_group1)+list(cb_group2)
    print(x)
    # gspec = pn.GridSpec(height_policy='max',sizing_mode='stretch_both')
    # if 'Banana' in x:
    #     gspec = tem
    # elif 'Apple' in x:
    #     gspec = plotly_violin
    # else:
    gspec = bokeh_pane
    return gspec


# gspec = pn.GridSpec(sizing_mode='stretch_both',width_policy='max')
#
# gspec[0, :3] = pn.Spacer(background='#FF0000')
# gspec[1:3, 0] = pn.Spacer(background='#0000FF')
# gspec[1:3, 1:3] = plotly_violin

# @pn.depends(select)
# def download_image(filetype):
#     print(filetype)
#
#
# fd = pn.widgets.FileDownload(
#     callback=download_image, filename='filtered_autompg.csv'
# )
# select = pn.widgets.Select(options=['.png', '.jpg', '.pdf'], width=100)




# button = pn.widgets.Button(name='Download Current Plot/s', button_type='primary',width=200)
# button.on_click(download_image)


pane1=pn.Column(
    pn.Row(
        # pn.Column(
        #     pn.widgets.FloatSlider(name='Number', margin=(10, 5, 5, 10)),
        #     pn.widgets.Select(name='Fruit', options=['Apple', 'Orange', 'Pear'], margin=(0, 5, 5, 10)),
        #     pn.widgets.Button(name='Run', margin=(5, 10, 10, 10)),
        # css_classes=['widget-box']),
        pn.Column(
            pn.pane.HTML('<p><b>DMA:</b></p>'),
            dma_button,
            pn.pane.HTML('<p><b>Headloss:</b></p>'),
            headloss_button,
            pn.pane.HTML('<p><b>Grouping:</b></p>'),
            grouping_button,
            pn.pane.HTML('<p><b>Plotting Options:</b></p>'),
            checkbox1,
            checkbox2,
            # plot_buttons,
            # pn.pane.HTML('<p><b>Download Image:</b></p>'),
            # pn.Row(button, select),
        ),
    bokeh_pane,
    #     pn.Tabs(
    #         ('CDF',bokeh_pane),
    #         ('hist',gspec),
    #         dynamic=True)
    ),
    # pn.pane.HTML('<p>Made by Alex Waldron<br><b>Last updated:</b> 03 April 2020</p>'),
    width_policy='max',sizing_mode='stretch_both'
)




# html_pane = pn.pane.HTML('hello world')



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

mypanel=pane1
def call_heroku():
    return mypanel

if __name__=='__main__':
    mypanel.show()