from flask import Flask, render_template

from bokeh.embed import server_document
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
import param
import panel as pn
from bokeh.server.server import Server
from tornado.ioloop import IOLoop

from bokeh.embed import components


from bokeh.sampledata.sea_surface_temperature import sea_surface_temperature


class SeaSurface(param.Parameterized):

    smoothing = param.Integer(0,bounds=(0, 30))

    def __init__(self, **params):
        super(SeaSurface, self).__init__(**params)
        self.df = sea_surface_temperature.copy()
        self.source = ColumnDataSource(data=self.df)

        self.plot = figure(x_axis_type='datetime', y_range=(0, 25), y_axis_label='Temperature (Celsius)',
                title="Sea Surface Temperature at 43.18, -70.43")

        self.plot.line('time', 'temperature', source=self.source)

    @param.depends('smoothing')
    def view(self):
        if self.smoothing == 0:
            data = self.df
        else:
            data = self.df.rolling('{0}D'.format(self.smoothing)).mean()

        self.source.data = ColumnDataSource(data=data).data

        return self.plot

    def panel(self):
        return pn.Row(self.param, self.view)


# uncomment to run app directly out of panel and comment Flask setup below
# sea = SeaSurface(name='Sea Surface')
# sea.panel().show()

# Flask setup
app = Flask(__name__)

def modify_doc(doc):
    sea = SeaSurface(name='Sea Surface')
    doc.add_root(sea.panel().get_root(doc))

# sea = SeaSurface(name='Sea Surface')


# @app.route('/')
# def homepage():
#
#     # #Get the data, from somewhere
#     # df = pd.read_csv('https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data',
#     #                  names=['sepal_length', 'sepal_width', 'petal_length', 'petal_width', 'class'])
#
#     # #Setup plot
#     # p = get_plot(df)
#     script, div = components(sea.panel().get_root())
#
#     #Render the page
#     return render_template('embed.html', script=script, template="Flask")

@app.route('/', methods=['GET'])
def bkapp_page():
    script = server_document('http://localhost:5006/bkapp')
    return render_template("embed.html", script=script, template="Flask")
#
#
def bk_worker():
    # Can't pass num_procs > 1 in this configuration. If you need to run multiple
    # processes, see e.g. flask_gunicorn_embed.py
    server = Server({'/bkapp': modify_doc})#, io_loop=IOLoop(), allow_websocket_origin=["127.0.0.1:8000"])
    server.start()
    # server.io_loop.start()
#
#
# from threading import Thread
# Thread(target=bk_worker).start()

def heroku_call():
    return app

