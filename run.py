# import app from wherever
from heroku import heroku_dash_example
from plotting_stuff import example_dash, example_panel, example_bokehflask

# for running flash
# from plotting_stuff import qtwidge

# get app
# app = heroku_dash_example.run_me()
# app = example_dash.heroku_call()
# app = example_bokehflask.heroku_call()

# app = heroku_dash_example.heroku_call()

# get server
# server = app.server # if dash
# server = app # if bokeh/panel
# app.debug = True
# app.run()

# pn = example_panel.heruko_call()



if __name__ == '__main__':
    # qtwidge.run_dash(app)
    # app.run_server(debug=True)

    pn = example_panel.heruko_call()
    pn.servable()
    # app.run()
    # app.debug = True
    # def run_bokeh(app):
    #     app.run(port=8000)
    # import threading
    # threading.Thread(target=run_bokeh, args=(app,), daemon=True).start()
