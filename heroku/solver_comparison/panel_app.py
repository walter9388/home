import pandas as pd
import panel as pn
import numpy as np
import param
import os

# import altair as alt

import seaborn as sns

import matplotlib as mpl
from bokeh.plotting import output_file, show
from bokeh.layouts import row
from bokeh.models import Legend, FactorRange

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
    df2=pd.read_csv('data2.csv',header=[0,1,2,3],index_col=[0,1])
    df3=pd.read_csv('data3.csv',header=[0,1,2,3],index_col=[0,1])
    df2_0=pd.read_csv('data2_initial.csv',header=[0,1,2,3],index_col=[0,1])
    df3_0=pd.read_csv('data3_initial.csv',header=[0,1,2,3],index_col=[0,1])
except:
    # data=pd.read_csv('data.csv',index_col=(0,1,2,3,4))
    df2=pd.read_csv('heroku/solver_comparison/data2.csv',header=[0,1,2,3],index_col=[0,1])
    df3=pd.read_csv('heroku/solver_comparison/data3.csv',header=[0,1,2,3],index_col=[0,1])
    df2_0=pd.read_csv('heroku/solver_comparison/data2_initial.csv',header=[0,1,2,3],index_col=[0,1])
    df3_0=pd.read_csv('heroku/solver_comparison/data3_initial.csv',header=[0,1,2,3],index_col=[0,1])

# df2_sorted=pd.DataFrame(np.sort(df2.loc['err_val'].values,axis=0),columns=df2.columns)
# df3_sorted=pd.DataFrame(np.sort(df3.loc['err_val'].values,axis=0),columns=df3.columns)


solvers=['L-BFGS-B','SCP']
colours=['green','red']

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
    value=list(df2.columns.levels[3])[-1],
    options=list(df2.columns.levels[3])[::-1],
    button_type='default')

PlotType = pn.widgets.Select(name='Plot Type:', options=['CDF', 'Error Bars','Violin','Summary'])

variable_map={
    'err050': '0.5m Error [%]',
    'err075': '0.75m Error [%]',
    'err200': '2m Error [%]',
    'err_train': 'Training Error',
    'err_val': 'Validation Error',
    'maxerr': '0.5m Error [m]',
    'objval': 'Objective Function Value',
    'regparams': 'Regularisation Hyper-Parameter',
    'time': 'Time (s)',
}
varmap=lambda x: [variable_map[x[i]] for i in range(len(x))]
inv_map = {v: k for k, v in variable_map.items()}

plot_variable = pn.widgets.Select(
    name='Plot Variable:',
    options=varmap(list(df2.index.levels[0].drop('gurobifail'))),
    value=variable_map['err_val'])

reg_or_not = pn.widgets.RadioBoxGroup(
    value='using regularisation',
    options=['using regularisation','no regularisation'],
    inline=True)

outliers_checkbox = pn.widgets.Checkbox(name='Remove Large Outliers',value=True)

show_c0 = pn.widgets.Checkbox(name='show c0 = cBWFL',value=False)

@pn.depends(dma_button,headloss_button,grouping_button,checkbox1,checkbox2,plot_variable,show_c0)
def bokeh_pane(dma,headloss,grouping,cb1,cb2,pv,sc):

    dma_button.disabled=False
    headloss_button.disabled=False
    grouping_button.disabled=False
    checkbox1.disabled=False
    checkbox2.disabled=False
    show_c0.disabled = False

    df2_sorted = pd.DataFrame(np.sort(df2.loc[inv_map[pv]].values, axis=0), columns=df2.columns)
    df3_sorted = pd.DataFrame(np.sort(df3.loc[inv_map[pv]].values, axis=0), columns=df3.columns)

    x, y, x_0, y_0 = [0,0], [0,0], [0,0], [0,0]
    for i in range(len(solvers)):
        x[i] = df2_sorted[(solvers[i].replace('-',''), dma, headloss, grouping)]
        y[i] = np.linspace(0, 100, len(x[i]))
        x_0[i] = df3_sorted[(solvers[i].replace('-',''), dma, headloss, grouping)]
        y_0[i] = np.linspace(0, 100, len(x_0[i]))


    # Set up plot
    if inv_map[pv] == 'regparams':
        p = figure(title='Randomised Starting Points CDF: BWFL - {} - {} - {}'.format(dma, headloss, grouping),
                   tools="reset,save,xwheel_zoom,xpan,hover",
                   active_scroll='xwheel_zoom',
                   y_range=(0, 100),
                   x_axis_label=pv,
                   y_axis_label='% tests',
                   x_axis_type='log'
                   )
    else:
        p = figure(title='Randomised Starting Points CDF: BWFL - {} - {} - {}'.format(dma, headloss, grouping),
                   tools="reset,save,xwheel_zoom,xpan,hover",
                   active_scroll='xwheel_zoom',
                   y_range=(0, 100),
                   x_axis_label=pv,
                   y_axis_label='% tests',
                   )

    # line 1
    for i in range(len(solvers)):
        if solvers[i] in cb1:
            if 'with reg' in cb2:
                p.line(x[i], y[i], line_width=3, line_alpha=0.6, color=colours[i], legend_label=solvers[i], name=solvers[i])
                if sc:
                    xx=list(df2_0.loc[inv_map[pv],(solvers[i].replace('-',''), dma, headloss, grouping)])
                    p.scatter(xx, np.interp(xx, x[i], y[i]), marker='x',size=15, line_width=3, line_color=colours[i],name=solvers[i]+'_BWFL',legend_label=solvers[i]+'_BWFL')
                    p.line([xx[0],xx[0]],[0,100], line_width=1, line_alpha=0.6, color=colours[i], name=solvers[i]+'_BWFL',legend_label=solvers[i]+'_BWFL')
            if 'no reg' in cb2:
                p.line(x_0[i], y_0[i], line_width=3, line_alpha=0.6, line_dash='dashed', color=colours[i], legend_label=solvers[i] + ' (no reg)', name=solvers[i] + ' (no reg)')
                if sc:
                    xx=list(df3_0.loc[inv_map[pv],(solvers[i].replace('-',''), dma, headloss, grouping)])
                    p.scatter(xx, np.interp(xx, x_0[i], y_0[i]), marker='x',size=15, line_width=3, line_color=colours[i],name=solvers[i]+'_BWFL (no reg)',legend_label=solvers[i]+'_BWFL (no reg)')
                    p.line([xx[0],xx[0]],[0,100], line_width=1, line_alpha=0.6, line_dash='dashed', color=colours[i], legend_label=solvers[i]+'_BWFL (no reg)', name=solvers[i]+'_BWFL (no reg)')


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

@pn.depends(dma_button,headloss_button,grouping_button,checkbox1,checkbox2,plot_variable,outliers_checkbox,reg_or_not,show_c0)
def plotly_violin(dma,headloss,grouping,cb1,cb2,pv,rm_outliers,rn,sc):

    dma_button.disabled=False
    headloss_button.disabled=False
    grouping_button.disabled=False
    show_c0.disabled = False

    # df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/violin_data.csv")
    pv_=pv
    fig = go.Figure()
    if rn == 'using regularisation':
        df = df2
    elif rn == 'no regularisation':
        df = df3
    temp = df.loc[inv_map[pv], (solvers[1].replace('-',''), dma, headloss, grouping)]
    temp2 = df.loc[inv_map[pv], (solvers[0].replace('-',''), dma, headloss, grouping)]

    if inv_map[pv] in ['err_val','err_train']:
        if rm_outliers:
            temp = temp[df.loc[inv_map[pv], (solvers[1].replace('-',''), dma, headloss, grouping)] < 10]
            temp2 = temp2[df.loc[inv_map[pv], (solvers[0].replace('-',''), dma, headloss, grouping)] < 10]
    elif inv_map[pv] == 'regparams':
        temp = temp.apply(lambda x: np.log10(x) if x != 0 else -16)
        temp2 = temp2.apply(lambda x: np.log10(x) if x != 0 else -16)
        pv_ = pv + ' [log10(ρ) where log10(0)=-16]'

    fig.add_trace(go.Violin(y=['-'.join([dma, headloss, grouping])]*temp2.shape[0],#list(zip(*temp.index))[:-1],
                            x=temp2.values,
                            legendgroup='LBFGSB', name='LBFGSB',
                            side='positive',
                            line_color='green')
                  )
    fig.add_trace(go.Violin(y=['-'.join([dma, headloss, grouping])]*temp.shape[0],#list(zip(*temp.index))[:-1],
                            x=temp.values,
                            legendgroup='SCP', name='SCP',
                            side='negative',
                            line_color='red')
                  )
    fig.update_traces(meanline_visible=True,orientation='h')
    if sc:
        for i in range(len(solvers)):
            xx = list(df2_0.loc[inv_map[pv], (solvers[i].replace('-', ''), dma, headloss, grouping)])
            if inv_map[pv]=='regparams':
                xx = list(df2_0.loc[inv_map[pv], (solvers[i].replace('-', ''), dma, headloss, grouping)].apply(lambda x: np.log10(x) if x != 0 else -16))
            fig.add_trace(go.Scatter(x=xx,
                                  y = ['-'.join([dma, headloss, grouping])],
                                  legendgroup='c_BWFL ('+solvers[i]+')', name = 'c_BWFL ('+solvers[i]+')',
                                  marker_color=colours[i], marker_line_color='black', marker_line_width=2,
                                  mode='markers',marker_symbol='x',marker_size=15)
                          )



    # if inv_map[pv]=='regparams':
    #     fig.update_layout(violingap=0, violinmode='overlay', yaxis=dict(range=(-1, 1)), margin=dict(l=0, r=0, t=0, b=0),
    #                       xaxis=dict(gridcolor='black'), xaxis_title=pv, plot_bgcolor='rgba(0, 0, 0, 0)',
    #                       legend_title='<b> Solver </b>', xaxis_type="log")
    # else:
    fig.update_layout(violingap=0, violinmode='overlay', yaxis=dict(range=(-1, 1)), margin=dict(l=0, r=0, t=0, b=0),
                      xaxis=dict(gridcolor='black'), xaxis_title=pv_, plot_bgcolor='rgba(0, 0, 0, 0)',
                      legend_title='<b> Solver </b>')

    return pn.pane.Plotly(fig,sizing_mode='stretch_width',width_policy='max')


@pn.depends(dma_button,headloss_button,grouping_button,checkbox1,checkbox2)
def plotly_boxplot(dma,headloss,grouping,checkbox1,checkbox2):

    df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/violin_data.csv")

    fig = go.Figure()
    temp=df2.loc['err_val', (solvers[1].replace('-',''), dma, headloss, grouping)][df2.loc['err_val', (solvers[1].replace('-',''), dma, headloss, grouping)] < 10]
    temp2 = df2.loc['err_val', (solvers[0].replace('-',''), dma, headloss, grouping)][df2.loc['err_val', (solvers[0].replace('-',''), dma, headloss, grouping)] < 10]
    # ['-'.join(df2.columns.values[i]) for i in range(len(df2.columns))]

    nn=['DMA1','DMA2']
    nnn=['DW','HW']
    nnnn=['nongrouped','grouped']


    for i in range(2):
        for j in range(2):
            for k in range(2):
                fig.add_trace(go.Box(y=['-'.join([nn[i],nnn[j],nnnn[k]])]*100,#['-'.join([dma, headloss, grouping])]*100,#list(zip(*temp.index))[:-1],
                                        x=df2.loc['err_val', (solvers[1].replace('-',''), nn[i], nnn[j], nnnn[k])][df2.loc['err_val', (solvers[1].replace('-',''), nn[i], nnn[j], nnnn[k])] < 10].values,#temp.values,
                                        legendgroup='SCP', name='SCP',
                                        # side='negative',
                                        line_color='blue')
                              )
                fig.add_trace(go.Box(y=['-'.join([nn[i],nnn[j],nnnn[k]])]*100,#['-'.join([dma, headloss, grouping])]*100,#list(zip(*temp.index))[:-1],
                                        x=df2.loc['err_val', (solvers[0].replace('-',''), nn[i], nnn[j], nnnn[k])][df2.loc['err_val', (solvers[0].replace('-',''), nn[i], nnn[j], nnnn[k])] < 10].values,#temp.values,
                                        legendgroup='LBFGSB', name='LBFGSB',
                                        # side='positive',
                                        line_color='orange')
                              )
    fig.update_traces(meanline_visible=True,orientation='h')
    fig.update_layout(violingap=0, violinmode='overlay',yaxis=dict(range=(-1,1)),margin=dict(l=0, r=0, t=0, b=0),xaxis=dict(gridcolor='black'),plot_bgcolor='rgba(0, 0, 0, 0)')
    # ‘paper_bgcolor’: ‘rgba(0, 0, 0, 0)’)

    return pn.pane.Plotly(fig,sizing_mode='stretch_both',width_policy='max')


@pn.depends(dma_button,headloss_button,grouping_button,checkbox1,checkbox2)
def ridge_plot(dma,headloss,grouping,checkbox1,checkbox2):
    import colorcet as cc
    from numpy import linspace
    from scipy.stats.kde import gaussian_kde

    from bokeh.io import output_file, show
    from bokeh.models import ColumnDataSource, FixedTicker, PrintfTickFormatter
    from bokeh.plotting import figure
    from bokeh.sampledata.perceptions import probly

    def ridge(category, data, scale=20):
        return list(zip([category] * len(data), scale * data))

    cats = list(reversed(probly.keys()))

    palette = [cc.rainbow[i * 15] for i in range(17)]

    x = linspace(-20, 110, 500)

    source = ColumnDataSource(data=dict(x=x))

    p = figure(y_range=cats, x_range=(-5, 105), toolbar_location=None)

    for i, cat in enumerate(reversed(cats)):
        pdf = gaussian_kde(probly[cat])
        y = ridge(cat, pdf(x))
        source.add(y, cat)
        p.patch('x', cat, color=palette[i], alpha=0.6, line_color="black", source=source)

    p.outline_line_color = None
    p.background_fill_color = "#efefef"

    p.xaxis.ticker = FixedTicker(ticks=list(range(0, 101, 10)))
    p.xaxis.formatter = PrintfTickFormatter(format="%d%%")

    p.ygrid.grid_line_color = None
    p.xgrid.grid_line_color = "#dddddd"
    p.xgrid.ticker = p.xaxis.ticker

    p.axis.minor_tick_line_color = None
    p.axis.major_tick_line_color = None
    p.axis.axis_line_color = None

    p.y_range.range_padding = 0.12

    return pn.pane.Bokeh(p)


@pn.depends(dma_button,headloss_button,grouping_button,checkbox1,checkbox2,reg_or_not,plot_variable,show_c0)
def splir_bar(dma,headloss,grouping,cb1,cb2,rn,pv,sc):

    dma_button.disabled=False
    headloss_button.disabled=False
    grouping_button.disabled=False
    checkbox1.disabled=True
    checkbox2.disabled=True
    show_c0.disabled = False

    if inv_map[pv] in ['err_val', 'err_train']:
        max_init_view = 10
    else:
        max_init_view = 1e100  # inf

    x=[[],[]]
    if rn == 'using regularisation':
        df = df2
    elif rn == 'no regularisation':
        df = df3
    for i in range(len(solvers)):
        x[i]=df.loc[inv_map[pv],(solvers[i].replace('-',''), dma, headloss, grouping)]

    temp=x[0]-x[1]
    cols = [colours[1] if temp[i] > 0 else colours[0] for i in range(temp.shape[0])]
    cols2 = [solvers[1] if temp[i] > 0 else solvers[0] for i in range(temp.shape[0])]

    # Set up plot
    p = figure(title='Error Bars: BWFL - {} - {} - {}'.format(dma,headloss,grouping),
               tools="reset,save,xwheel_zoom,xpan,hover",
               active_scroll='xwheel_zoom',
               y_range=(0.5,x[0].shape[0]+0.5),
               x_range=(min(x[0].append(x[1])), min(max_init_view,max(x[0].append(x[1])))),
               x_axis_label=pv,
               y_axis_label='# Set',
               )

    p2 = figure(title='Error Bars (diff): BWFL - {} - {} - {}'.format(dma,headloss,grouping),
               tools="reset,save,xwheel_zoom,xpan,hover",
               active_scroll='xwheel_zoom',
               y_range=(0.5,x[0].shape[0]+0.5),
               x_range=(-min(max_init_view,max(temp.apply(abs))),min(max_init_view,max(temp.apply(abs)))),
               x_axis_label='Residual',
               y_axis_label='# Set',
               )

    p.hover.tooltips=[
        ('Set', '@y'),
        (solvers[0] + ' error', '@left'),
        (solvers[1] + ' error', '@right'),
        ('abs_err','@absdiff'),
    ]
    p2.hover.tooltips=p.hover.tooltips

    data=dict(left=x[0],
              right=x[1],
              diff=temp,
              absdiff=temp.apply(abs),
              y=np.arange(1,x[0].shape[0] + 1),
              colours=cols,
              legend_label=cols2,
              )

    p.hbar(y='y', left='left', right='right', height=1, fill_color='colours', line_color='black',legend='legend_label',source=data)
    p2.hbar(y='y', right='diff', height=1, fill_color='colours', line_color='black', legend='legend_label', source=data)

    if sc:
        for i in range(len(solvers)):
            xx = list(df2_0.loc[inv_map[pv], (solvers[i].replace('-', ''), dma, headloss, grouping)])
            p.line([xx[0], xx[0]], [0, 100], line_width=4, line_alpha=0.6, color=colours[i], name=solvers[i] + '_BWFL')

    # p.legend.title = 'Better Solver'
    # p.legend.location = 'best'
    # p.legend.orientation = 'horizontal'
    # p.legend.location = (1, -30)

    return pn.pane.Bokeh(row(p,p2),sizing_mode='stretch_both', width_policy='max')

@pn.depends(dma_button,headloss_button,grouping_button,checkbox1,checkbox2,reg_or_not,plot_variable,show_c0)
def summary_bar(dma,headloss,grouping,cb1,cb2,rn,pv,sc):

    dma_button.disabled=True
    headloss_button.disabled=True
    grouping_button.disabled=True
    checkbox1.disabled=True
    checkbox2.disabled=True
    show_c0.disabled=True

    x=[[],[]]
    if rn == 'using regularisation':
        df = df2
    elif rn == 'no regularisation':
        df = df3
    x=[]
    for i in [min,max]:
        # x.append(df.loc[inv_map[pv]].apply(i).values.reshape(2,8).T.reshape(16,))
        x.append(df.loc[inv_map[pv]].apply(i).values)

    if inv_map[pv] in ['err_val','err_train']:
        max_init_view = 10
    else:
        max_init_view = 1e100 # inf

    coltup=[('-'.join(list(df2.loc['err_val'].columns.droplevel(0))[i]),list(df2.columns.droplevel([1,2,3]))[i]) for i in range(16)]

    temp=x[0]-x[1]

    cols = [colours[1] if coltup[i][1]=='SCP' else colours[0] for i in range(temp.shape[0])]
    cols2 = [solvers[1] if coltup[i][1]=='SCP' else solvers[0] for i in range(temp.shape[0])]

    # Set up plot
    # if inv_map[pv] == 'regparams':
    #     p = figure(title='Error Bars: BWFL - {} - {} - {}'.format(dma,headloss,grouping),
    #                tools="reset,save,xwheel_zoom,xpan,hover",
    #                active_scroll='xwheel_zoom',
    #                x_range=FactorRange(*coltup),#['-'.join(i) for i in list(df2.loc['err_val'].columns)],
    #                y_range=(min(np.hstack([x[0],x[1]])), min(max_init_view,max(np.hstack([x[0],x[1]])))),
    #                x_axis_label=pv,
    #                y_axis_label='# Set',
    #                y_axis_type='log'
    #                )
    # else:
    p = figure(title='Error Bars: BWFL - {} - {} - {}'.format(dma,headloss,grouping),
               tools="reset,save,ywheel_zoom,ypan,hover",
               active_scroll='ywheel_zoom',
               x_range=FactorRange(*coltup),#['-'.join(i) for i in list(df2.loc['err_val'].columns)],
               y_range=(min(np.hstack([x[0],x[1]])), min(max_init_view,max(np.hstack([x[0],x[1]])))),
               # x_axis_label=pv,
               y_axis_label=pv,
               )

    p.hover.tooltips=[
        ('Test', '@y'),
        ('Min', '@left'),
        ('Max', '@right'),
        ('Range','@absdiff'),
    ]

    data=dict(left=x[0],
              right=x[1],
              diff=temp,
              absdiff=np.abs(temp),
              y=coltup,#['-'.join(i) for i in list(df2.loc['err_val'].columns)],
              colours=cols,
              legend_label=cols2,
              xtemp=list(df2_0.loc['err_val'].values[0])+list(df2_0.loc['err_val'].values[0])
              )

    # p.hbar(y='y', left='left', right='right', height=1, line_color='black',source=data)
    p.vbar(x='y', bottom='left', top='right', width=1, line_color='black', fill_color='colours',source=data)

    p.xaxis.major_label_orientation = "vertical"

    p.hover.mode = 'vline'
    # p.legend.title = 'Better Solver'
    # p.legend.location = 'best'
    # p.legend.orientation = 'horizontal'
    # p.legend.location = (1, -30)

    # if sc:
    #     # xx = list(df2_0.loc['err_val'].values[0])
    #     p.s(x='y', y='xtemp', marker='x',size=15, line_width=3, line_color=colours[i],name=solvers[i]+'_BWFL (no reg)',legend_label=solvers[i]+'_BWFL (no reg)',source=data)


    return pn.pane.Bokeh(p,sizing_mode='stretch_both', width_policy='max')

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
cb_group2 = pn.widgets.CheckButtonGroup(name='Check Button Group', value=[], options=['Apple1', 'Banana1'],margin=0)
plot_buttons=pn.Column(
    cb_group1,
    cb_group2
)
# dd=pn.pane.Bokeh(headloss_button)


# radio_button_group.js_link(p.x,value=df2[('DMA1','DW','nongrouped')])

# @pn.depends(cb_group1,cb_group2)
# def gridspec(cb_group1,cb_group2):
#     x=list(cb_group1)+list(cb_group2)
#     print(x)
#     # gspec = pn.GridSpec(height_policy='max',sizing_mode='stretch_both')
#     if 'Apple' in x:
#         gspec = plotly_violin
#     elif 'Banana' in x:
#         gspec = splir_bar
#     else:
#         gspec = bokeh_pane
#     return gspec

@pn.depends(PlotType)
def gridspec2(pt):
    # gspec = pn.GridSpec(height_policy='max',sizing_mode='stretch_both')
    if pt == 'Violin':
        gspec = plotly_violin
    elif pt == 'Error Bars':
        gspec = splir_bar
    elif pt == 'Summary':
        gspec = summary_bar
    else:
        gspec = bokeh_pane
    return gspec


# gspec = pn.GridSpec(sizing_mode='stretch_both',width_policy='max')
#
# gspec[0, :3] = pn.Spacer(background='#FF0000')
# gspec[1:3, 0] = pn.Spacer(background='#0000FF')
# gspec[1:3, 1:3] = plotly_violin


# todo: add download button
# @pn.depends(select)
# def download_image(filetype):
#     print(filetype)
#
# fd = pn.widgets.FileDownload(
#     callback=download_image, filename='filtered_autompg.csv'
# )
# select = pn.widgets.Select(options=['.png', '.jpg', '.pdf'], width=100)
# button = pn.widgets.Button(name='Download Current Plot/s', button_type='primary',width=200)
# button.on_click(download_image)



@pn.depends(PlotType,plot_variable)
def control_panel(pt,pv):
    cont = pn.Column(
        pn.pane.HTML('<p><b>DMA:</b></p>'),
        dma_button,
        pn.pane.HTML('<p><b>Headloss:</b></p>'),
        headloss_button,
        pn.pane.HTML('<p><b>Grouping:</b></p>'),
        grouping_button,
        pn.pane.HTML('<p><b>Plotting Options:</b></p>'),
        # plot_buttons,
        show_c0,
        PlotType,
        # pn.pane.HTML('<p><b>Download Image:</b></p>'),
        # pn.Row(button, select),
        plot_variable,
    )
    if pt == 'Error Bars':
        cont.append(reg_or_not)
    if pt == 'Summary':
        cont.append(reg_or_not)
    elif pt == 'CDF':
        # cont.append(plot_variable)
        cont.append(checkbox1)
        cont.append(checkbox2)
    elif pt =='Violin':
        cont.append(reg_or_not)
        if inv_map[pv] in ['err_val', 'err_train']:
            cont.append(outliers_checkbox)

    return cont


pane1=pn.Column(
    pn.Row(
        # pn.Column(
        #     pn.widgets.FloatSlider(name='Number', margin=(10, 5, 5, 10)),
        #     pn.widgets.Select(name='Fruit', options=['Apple', 'Orange', 'Pear'], margin=(0, 5, 5, 10)),
        #     pn.widgets.Button(name='Run', margin=(5, 10, 10, 10)),
        # css_classes=['widget-box']),
        control_panel,
    gridspec2,
    #     pn.Tabs(
    #         ('CDF',bokeh_pane),
    #         ('hist',gspec),
    #         dynamic=True)
    ),
    pn.pane.HTML('<p>Made by Alex Waldron<br><b>Last updated:</b> 06 April 2020</p>'),
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
    pass
    # mypanel.show()