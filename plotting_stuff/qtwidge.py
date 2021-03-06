import sys
import threading
from PyQt5.QtCore import QUrl, QSize
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QSizePolicy
from PyQt5.QtGui import QPalette, QColor, QIcon
import ctypes
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from plotting_stuff import run_servers


class Color(QWidget):

    def __init__(self, color, *args, **kwargs):
        super(Color, self).__init__(*args, **kwargs)
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)


class Main(QWidget):

    def __init__(self,url):
        self.app = QApplication(sys.argv)
        super().__init__()

        self.initUI(url)

        self.show()
        sys.exit(self.app.exec())

    def initUI(self,url):
        self.setWindowTitle(u'\u00A9Waldron2020')
        self.setWindowIcon(QIcon('test.png'))
        myappid = u'mycompany.myproduct.subproduct.version'  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        self.web = QWebEngineView()
        # self.web.setUrl(QUrl("http://127.0.0.1:8050"))
        # self.web.setUrl(QUrl("https://google.com"))
        self.web.setUrl(QUrl(url))
        self.web.setZoomFactor(2)

        self.lay = QVBoxLayout(self)
        self.lay.addWidget(self.web)

        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)

    def sizeHint(self):
        return QSize(2000, 1000)

    def heightForWidth(self, width):
        return width * 1.5


def rundashqt(app):
    threading.Thread(target=run_dash, args=(app,), daemon=True).start()
    Main('http://127.0.0.1:8050')

def runbokehqt(app):
    threading.Thread(target=run_bokeh, args=(app,), daemon=True).start()
    Main('http://127.0.0.1:8000')

def run_bokeh(app):
    # app.run(port=8000)
    run_servers.run_bokeh(app)

def run_dash(app):
    # app.run_server(debug=False)
    run_servers.run_dash(app)


def runpanelqt(pn):

    from flask import Flask, render_template
    from bokeh.embed import server_document
    from bokeh.server.server import Server
    from tornado.ioloop import IOLoop

    # Flask setup
    app = Flask(__name__)

    def modify_doc(doc):
        doc.add_root(pn.get_root(doc))

    @app.route('/', methods=['GET'])
    def bkapp_page():
        script = server_document('http://localhost:5006/bkapp')
        return render_template("embed.html", script=script, template="Flask")

    def bk_worker():
        # Can't pass num_procs > 1 in this configuration. If you need to run multiple
        # processes, see e.g. flask_gunicorn_embed.py
        server = Server({'/bkapp': modify_doc}, io_loop=IOLoop(), allow_websocket_origin=["127.0.0.1:8000"])
        server.start()
        server.io_loop.start()

    from threading import Thread
    Thread(target=bk_worker).start()

    threading.Thread(target=run_bokeh, args=(app,), daemon=True).start()
    Main('http://127.0.0.1:8000')


if __name__ == '__main__':
    data = [
        {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
        {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'}
    ]
    layout = {
        'title': 'Dash Data Visualization',
    }

    app = dash.Dash()
    app.layout = html.Div(children=[
        html.H1(children='Hello Dash'),
        html.Div(children='''
                Dash: A web application framework for Python.
            '''),
        dcc.Graph(
            id='example-graph',
            figure={
                'data': data,
                'layout': layout
            }
        )
    ])

    rundashqt(app)

