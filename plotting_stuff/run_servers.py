

def run_bokeh(app):
    app.run(port=8000)

def run_dash(app):
    app.run_server(debug=False)

def run_panel(pn):
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

    # from threading import Thread
    # Thread(target=bk_worker).start()

    return bk_worker


def run_panel2(pn):
    import flask
    from bokeh.embed import server_document, components
    from bokeh.server.server import Server
    from bokeh.plotting import figure
    from bokeh.resources import INLINE
    from bokeh.util.string import encode_utf8

    # Flask setup
    app = flask.Flask(__name__)

    colors = {
        'Black': '#000000',
        'Red': '#FF0000',
        'Green': '#00FF00',
        'Blue': '#0000FF',
    }

    def getitem(obj, item, default):
        if item not in obj:
            return default
        else:
            return obj[item]

    @app.route("/")
    def polynomial():
        """ Very simple embedding of a polynomial chart
        """

        # Grab the inputs arguments from the URL
        args = flask.request.args

        # Get all the form arguments in the url with defaults
        color = getitem(args, 'color', 'Black')
        _from = int(getitem(args, '_from', 0))
        to = int(getitem(args, 'to', 10))

        # Create a polynomial line graph with those arguments
        x = list(range(_from, to + 1))
        fig = figure(title="Polynomial")
        fig.line(x, [i ** 2 for i in x], color=colors[color], line_width=2)

        js_resources = INLINE.render_js()
        css_resources = INLINE.render_css()

        script, div = components(fig)
        html = flask.render_template(
            'embed.html',
            plot_script=script,
            plot_div=div,
            js_resources=js_resources,
            css_resources=css_resources,
            color=color,
            _from=_from,
            to=to
        )
        return encode_utf8(html)

    app.run()